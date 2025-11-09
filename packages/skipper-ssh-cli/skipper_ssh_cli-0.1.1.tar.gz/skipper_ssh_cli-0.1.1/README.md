# Skipper 🛶  
**Jump through your servers, not your configs.**  
CLI minimalista para gestionar y conectar a servidores vía SSH usando aliases y rutas a PEMs — **sin tocar** `~/.ssh/config`.

---

## 🚀 Why Skipper
- **Rápido**: `skipper connect web-01` y listo.
- **Seguro**: no guarda claves, solo **rutas** a tus `.pem`; permisos `600` en config.
- **Git-friendly**: JSON plano, versionable (opcional).
- **Enterprise-ready**: soporte de **bastion/ProxyJump** y flags SSH extra.

---

## ✨ Features
- Registro de hosts por **alias** (IP/FQDN, usuario, puerto, PEM).
- **Bastion/jump host** por alias o `user@host:port`.
- **Launcher interactivo** (`skipper menu`) con integración **fzf** si está disponible.
- **Extras SSH**: port-forward, compresión, etc., pasándolos tras `--`.

---

## 🧩 Requisitos
- Python **3.10+**
- (Opcional) `fzf` para el menú interactivo.

---

## 📦 Instalación (recomendado con pipx)
> En macOS: `brew install pipx && pipx ensurepath`

```bash
# desde el repo del proyecto
pipx install .
# o directo desde GitHub cuando publiques
# pipx install git+https://github.com/RchrdMrtnz/skipper.git

# comprobar
skipper --help
```

### Desarrollo local
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
skipper --help
```

---

## 🔐 Recomendación: centraliza tus PEMs
Mantén tus llaves en una carpeta privada y con permisos estrictos.

```bash
mkdir -p ~/.pem
# mueve tus .pem allí (confirma si pregunta)
for f in ~/*.pem; do [ -f "$f" ] && mv -i "$f" ~/.pem/; done
chmod 600 ~/.pem/*.pem
```

---

## ⚙️ Uso básico

### Agregar un host
```bash
skipper add   --alias web-01   --hostname 54.12.34.56   --user ubuntu   --pem ~/.pem/web-01.pem
```

### Listar hosts
```bash
skipper ls
```

### Conectarte por alias
```bash
skipper connect web-01
```

### Pasar flags extra a SSH (ej. port-forward)
```bash
skipper connect web-01 -- -L 5433:localhost:5432
```

### Eliminar un host
```bash
skipper rm web-01
```

---

## 🛰️ Bastion / ProxyJump
Define primero el bastion y luego el destino privado:

```bash
# bastion público
skipper add   --alias bastion   --hostname 3.88.77.66   --user ubuntu   --pem ~/.pem/bastion.pem

# host en red privada, saltando por bastion
skipper add   --alias db-priv   --hostname 10.0.2.15   --user ubuntu   --pem ~/.pem/db.pem   --bastion bastion

# conectar (Skipper usa -J debajo)
skipper connect db-priv
```

> Tip: también puedes usar `--proxy-jump "user@host:port"` si no quieres referenciar por alias.

---

## 🎛️ Menú interactivo
```bash
skipper menu
```
- Si tienes `fzf`, tendrás búsqueda difusa.
- Sin `fzf`, verás un selector simple en consola.

---

## 🧰 Comandos disponibles
```text
skipper add        # agrega/actualiza un host (alias, hostname, user, port, pem, bastion)
skipper ls         # lista hosts
skipper rm <alias> # elimina host por alias
skipper connect <alias> [-- <extras ssh>]
skipper menu       # launcher interactivo (fzf si existe)
skipper edit       # abre el archivo de configuración en tu $EDITOR
```

---

## 🗂️ Dónde se guarda la config
- Ruta por defecto: `~/.config/skipper/hosts.json` ( permisos `600` ).
- Overwrite vía variable de entorno:
```bash
export SKIPPER_CONFIG="$PWD/infra/skipper.hosts.json"
```
> Ideal si quieres versionarlo (o cifrarlo con `sops/age`) en tu repo de infraestructura.

---

## 🧹 Limpieza de `known_hosts` (cuando cambia la huella)
Si rotaste máquina/IP y ves el clásico warning:
```bash
ssh-keygen -R <IP>   # ej: ssh-keygen -R 44.218.145.76
skipper connect <alias>
```

---

## 🔒 Seguridad
- Skipper **no** almacena material de clave privada, solo **rutas** a tus `.pem`.
- Asegura permisos:
  ```bash
  chmod 600 ~/.pem/*.pem
  ```
- Si versionas config, considera cifrar `SKIPPER_CONFIG` con `sops/age`.

---

## 🛣️ Roadmap
- Tags y filtros (`skipper ls --tag prod`).
- Plantillas de túneles (`skipper tunnels add ...`).
- `skipper test <alias>` (sanity SSH/latencia).
- Import puntual desde `~/.ssh/config`.

---

## 🧪 Smoke test de ejemplo
```bash
# públicos
skipper add --alias test    --hostname 11.11.11.11 --user ubuntu --pem ~/.pem/test.pem


skipper ls
skipper connect n8n-momentum
skipper connect redis-momentum -- -L 6380:localhost:6379
```

---

## 📄 Licencia
GPL-3.0 — ver [`LICENSE`](./LICENSE).

---

## 🙌 Contribuciones
PRs bienvenidos. Mantén el estilo: Typer + Pydantic, tests simples y mensajes de commit claros (`feat:`, `fix:`, `docs:`).

---

**Skipper** — _jump through your servers, not your configs._ 🛶
