#!/usr/bin/env python3
from __future__ import annotations
import os, stat, subprocess, sys
from pathlib import Path
from typing import List, Optional

import typer
from pydantic import BaseModel, Field, field_validator
from rich import print as rprint
from rich.table import Table

app = typer.Typer(add_completion=False, help="Skipper: jump through servers, not configs.")

# ---------- Modelos ----------
class Host(BaseModel):
    alias: str
    hostname: str                 # IP o FQDN
    user: Optional[str] = None
    port: Optional[int] = None
    pem: str                      # ruta al .pem
    bastion: Optional[str] = None # alias o "user@host[:port]"
    proxy_jump: Optional[str] = None
    extra_ssh_opts: List[str] = Field(default_factory=list)

    @field_validator("port")
    @classmethod
    def _valid_port(cls, v):
        if v is not None and not (1 <= v <= 65535):
            raise ValueError("port must be 1..65535")
        return v

class HostsFile(BaseModel):
    version: int = 1
    hosts: List[Host] = Field(default_factory=list)

# ---------- Config ----------
APP_ENV_VAR = "SKIPPER_CONFIG"   # permite override del path (seguro para GitOps)
APP_DIRNAME = "skipper"          # ~/.config/skipper/hosts.json

def _config_path() -> Path:
    env = os.getenv(APP_ENV_VAR)
    if env:
        return Path(env).expanduser().resolve()
    xdg = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
    return (xdg / APP_DIRNAME / "hosts.json").resolve()

def _ensure_config() -> tuple[Path, HostsFile]:
    cfg = _config_path()
    cfg.parent.mkdir(parents=True, exist_ok=True)
    if not cfg.exists():
        data = HostsFile()
        _write_config(cfg, data)
        return cfg, data
    data = HostsFile.model_validate_json(cfg.read_text())
    return cfg, data

def _write_config(cfg: Path, data: HostsFile) -> None:
    cfg.write_text(data.model_dump_json(indent=2))
    os.chmod(cfg, stat.S_IRUSR | stat.S_IWUSR)  # 600

def _find_host(data: HostsFile, alias: str) -> Optional[Host]:
    for h in data.hosts:
        if h.alias == alias:
            return h
    return None

def _resolve(p: str) -> Path:
    return Path(p).expanduser().resolve()

# ---------- SSH Runner ----------
def _run_ssh(host: Host, data: HostsFile, extra: List[str]) -> None:
    if not host.hostname:
        typer.secho("hostname requerido", err=True, fg=typer.colors.RED); raise typer.Exit(1)
    if not host.pem:
        typer.secho("pem requerido", err=True, fg=typer.colors.RED); raise typer.Exit(1)

    pem_path = _resolve(host.pem)
    if not pem_path.exists():
        typer.secho(f"PEM no encontrado: {pem_path}", err=True, fg=typer.colors.RED); raise typer.Exit(1)

    proxy_jump = host.proxy_jump
    if not proxy_jump and host.bastion:
        bast = _find_host(data, host.bastion)
        if bast:
            u = f"{bast.user}@" if bast.user else ""
            p = f":{bast.port}" if bast.port else ""
            proxy_jump = f"{u}{bast.hostname}{p}"
        else:
            proxy_jump = host.bastion  # ya viene como user@host[:port]

    dest_user = f"{host.user}@" if host.user else ""
    dest = f"{dest_user}{host.hostname}"

    args: List[str] = [
        "ssh",
        "-i", str(pem_path),
        "-o", "IdentitiesOnly=yes",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", "ServerAliveInterval=30",
        "-o", "ServerAliveCountMax=3",
    ]
    if host.port: args += ["-p", str(host.port)]
    if proxy_jump: args += ["-J", proxy_jump]
    if host.extra_ssh_opts: args += host.extra_ssh_opts
    if extra: args += extra
    args += [dest]

    rprint(f"[grey50]> {' '.join(a if ' ' not in a else repr(a) for a in args)}")
    os.execvp(args[0], args)  # reemplaza el proceso actual por ssh

# ---------- Comandos ----------
@app.command("add")
def add(
    alias: Optional[str] = typer.Option(None, "--alias", "-a", help="Nombre único (p.ej. web-01)"),
    hostname: Optional[str] = typer.Option(None, "--hostname", "-H", help="IP/FQDN"),
    user: Optional[str] = typer.Option(None, "--user", "-u", help="ubuntu, ec2-user, root..."),
    port: Optional[int] = typer.Option(None, "--port", "-p", help="Puerto SSH (default 22)"),
    pem: Optional[str] = typer.Option(None, "--pem", "-k", help="Ruta al .pem"),
    bastion: Optional[str] = typer.Option(None, "--bastion", "-b", help="Alias o user@host[:port]"),
    proxy_jump: Optional[str] = typer.Option(None, "--proxy-jump", help="Override directo de -J"),
):
    """
    Agrega o actualiza un host. Si faltan datos, los pide por stdin (interactivo).
    """
    cfg, data = _ensure_config()

    def _ask(msg: str) -> str:
        typer.echo(msg + ": ", nl=False)
        return sys.stdin.readline().strip()

    alias = alias or _ask("Alias")
    hostname = hostname or _ask("Hostname/IP")
    pem = pem or _ask("Ruta PEM (~ permitido)")
    if user is None:
        u = _ask("User (opcional, Enter para omitir)")
        user = u or None
    if port is None:
        p = _ask("Port (opcional, Enter=22)")
        port = int(p) if p.strip() else None
    if bastion is None:
        b = _ask("Bastion (alias o user@host[:port], opcional)")
        bastion = b or None

    record = Host(alias=alias, hostname=hostname, user=user, port=port, pem=pem,
                  bastion=bastion, proxy_jump=proxy_jump)

    idx = next((i for i, h in enumerate(data.hosts) if h.alias == alias), -1)
    if idx >= 0:
        data.hosts[idx] = record
        rprint(f"[yellow]Actualizado[/]: {alias}")
    else:
        data.hosts.append(record)
        rprint(f"[green]Agregado[/]: {alias}")
    _write_config(cfg, data)
    rprint(f"[grey50]Config: {cfg}[/]")

@app.command("ls")
def ls_() -> None:
    """
    Lista los hosts registrados.
    """
    cfg, data = _ensure_config()
    if not data.hosts:
        rprint("No hay hosts. Usa `skipper add`.")
        raise typer.Exit()
    table = Table(title="Skipper hosts")
    table.add_column("Alias", style="cyan")
    table.add_column("Destino")
    table.add_column("PEM")
    table.add_column("Jump")
    for h in sorted(data.hosts, key=lambda x: x.alias):
        dest = f"{(h.user + '@') if h.user else ''}{h.hostname}{(':'+str(h.port)) if h.port else ''}"
        j = h.proxy_jump or h.bastion or ""
        table.add_row(h.alias, dest, h.pem, j)
    rprint(table)
    rprint(f"[grey50]Config: {cfg}[/]")

@app.command("rm")
def rm(alias: str) -> None:
    """
    Elimina un host por alias.
    """
    cfg, data = _ensure_config()
    before = len(data.hosts)
    data.hosts = [h for h in data.hosts if h.alias != alias]
    if len(data.hosts) < before:
        _write_config(cfg, data)
        rprint(f"[green]Eliminado[/]: {alias}")
    else:
        rprint(f"[yellow]No existe[/]: {alias}")

@app.command("connect", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def connect(alias: str) -> None:
    """
    Conecta a un host por alias. Pasa flags extra a ssh después de `--`.
    Ej: skipper connect db -- -L 5433:localhost:5432
    """
    argv = sys.argv
    extras: List[str] = []
    if "--" in argv:
        idx = argv.index("--")
        extras = argv[idx+1:]
    _, data = _ensure_config()
    host = _find_host(data, alias)
    if not host:
        rprint(f"[red]Alias no encontrado[/]: {alias}")
        raise typer.Exit(1)
    _run_ssh(host, data, extras)

@app.command("menu")
def menu() -> None:
    """
    Launcher interactivo. Usa fzf si está disponible; si no, menú básico.
    """
    _, data = _ensure_config()
    if not data.hosts:
        rprint("No hay hosts. Usa `skipper add`.")
        raise typer.Exit()
    aliases = sorted(h.alias for h in data.hosts)
    has_fzf = subprocess.run(["bash", "-lc", "command -v fzf >/dev/null 2>&1"]).returncode == 0
    if has_fzf:
        joined = " ".join([f"'{a}'" for a in aliases])
        res = subprocess.run(["bash", "-lc", f"printf '%s\n' {joined} | fzf --prompt='Select host> ' --height=40%"],
                             capture_output=True, text=True)
        choice = res.stdout.strip()
        if not choice:
            raise typer.Exit()
        host = _find_host(data, choice)
        _run_ssh(host, data, extra=[])
    else:
        rprint("Selecciona host:")
        for i, a in enumerate(aliases, 1):
            rprint(f"{i}. {a}")
        sel = input("> ").strip()
        try:
            idx = int(sel) - 1
            assert 0 <= idx < len(aliases)
        except Exception:
            rprint("[red]Selección inválida[/]"); raise typer.Exit(1)
        host = _find_host(data, aliases[idx])
        _run_ssh(host, data, extra=[])
