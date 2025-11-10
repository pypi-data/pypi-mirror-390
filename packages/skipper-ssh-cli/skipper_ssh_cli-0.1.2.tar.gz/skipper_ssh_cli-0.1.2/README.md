# Skipper 🛶  
**Jump through your servers, not your configs.**  
A minimalist CLI tool to manage and connect to SSH servers using aliases and PEM file paths — **without touching** your `~/.ssh/config`.

## 🚀 Why Skipper
- **Fast**: Just run `skipper connect web-01` and you're in.
- **Secure**: Doesn’t store keys, only **paths** to your `.pem` files. Config file uses strict `600` permissions.
- **Git-friendly**: Plain JSON config, optionally versionable.
- **Enterprise-ready**: Supports **bastion/ProxyJump**, SSH flags, and PEM routing.

## ✨ Features
- Register hosts via **alias** (IP/FQDN, user, port, PEM).
- Support for **bastion/jump hosts** via alias or `user@host:port`.
- Interactive **launcher** (`skipper menu`) with optional `fzf` integration.
- Pass **extra SSH flags** after `--`, e.g., port forwarding or compression.

## 🧩 Requirements
- Python **3.10+**
- (Optional) [`fzf`](https://github.com/junegunn/fzf`) for enhanced interactive menus

## 📦 Installation (recommended via `pipx`)
> macOS: `brew install pipx && pipx ensurepath`
```bash

pipx install .
```
or directly from GitHub:

```bash
pipx install git+https://github.com/RchrdMrtnz/skipper.git
```
Check installation:

```bash
skipper --help
```
### Local development

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
skipper --help
```
## 🔐 Recommendation: Centralize your PEMs

Keep your `.pem` files in a private, secured folder:
```bash
mkdir -p ~/.pem
for f in ~/*.pem; do [ -f "$f" ] && mv -i "$f" ~/.pem/; done
chmod 600 ~/.pem/*.pem
```
## ⚙️ Basic Usage
Add a host:
```bash
skipper add --alias web-01 --hostname 54.12.34.56 --user ubuntu --pem ~/.pem/web-01.pem
```
List hosts:
```bash
skipper ls
```
Connect:
```bash
skipper connect web-01
```
Pass extra SSH flags:
```bash
skipper connect web-01 -- -L 5433:localhost:5432
```
Remove:
```bash
skipper rm web-01
```
## 🛰️ Bastion / ProxyJump
```bash
skipper add --alias bastion --hostname 3.88.77.66 --user ubuntu --pem ~/.pem/bastion.pem
skipper add --alias db-priv --hostname 10.0.2.15 --user ubuntu --pem ~/.pem/db.pem --bastion bastion
skipper connect db-priv
```
You can also use:
```bash
--proxy-jump "user@host:port"
```
## 🎛️ Interactive Menu
```bash
skipper menu
```
- If `fzf` is installed, fuzzy-search menu is used.
- Otherwise, a simple console selector is shown.
## 🧰 Commands
```text
skipper add
skipper ls
skipper rm <alias>
skipper connect <alias> [-- <ssh flags>]
skipper menu
skipper edit
```
## 🗂️ Configuration
Default: `~/.config/skipper/hosts.json` (`600` perms)  
Override via:
```bash
export SKIPPER_CONFIG="$PWD/infra/skipper.hosts.json"
```
## 🔒 Security
- No private key material stored — only file paths
- Enforce strict PEM permissions:
```bash
chmod 600 ~/.pem/*.pem
```
- If versioning config, consider encrypting `SKIPPER_CONFIG`
## 🛣️ Roadmap
- Tags and filters
- Tunnel templates
- `skipper test <alias>`
- Import from `~/.ssh/config`
## 🧪 Example Smoke Test
```bash
skipper add --alias test --hostname 11.11.11.11 --user ubuntu --pem ~/.pem/test.pem
skipper ls
skipper connect test
skipper connect redis-momentum -- -L 6380:localhost:6379
```
## 📄 License
GPL-3.0 — see `LICENSE`
## 🙌 Contributing
PRs welcome. Follow Typer + Pydantic style, simple tests, clear commits (`feat:`, `fix:`, `docs:`).
**Skipper** — _jump through your servers, not your configs._ 🛶