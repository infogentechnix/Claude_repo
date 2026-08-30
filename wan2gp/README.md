# Wan2GP GPU Setup

Instructions for standing up [Wan2GP](https://github.com/deepbeepmeep/Wan2GP) on a GPU machine and exposing its web UI to the network.

## Manual setup

```bash
git clone https://github.com/deepbeepmeep/Wan2GP
cd Wan2GP
./install.sh                          # or install.bat on Windows
python wgp.py --listen --server-name 0.0.0.0   # binds to all interfaces
```

- `--listen` makes the server reachable from the local network (not just `localhost`).
- `--server-name 0.0.0.0` binds to all network interfaces.
- `--server-port <port>` selects the port (defaults to a random free port if unset).

The UI is served over plain HTTP with no authentication by default — only bind to
`0.0.0.0` on a trusted network or behind a firewall/reverse proxy you control.

## Scripted setup

`setup.sh` automates the steps above:

```bash
./setup.sh [install-dir] [port]
```

- `install-dir` — where to clone the repo (default: `~/Wan2GP`)
- `port` — port for the web UI (default: `7860`)

Re-running the script skips the clone step if the target directory already contains
a Wan2GP checkout.
