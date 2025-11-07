import os, subprocess, sys, json, shutil, socket, time
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
PROJECTS_DIR = BASE / 'projects'
CONFIG_PATH = BASE / 'config.json'

def ensure_projects_dir():
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    if not CONFIG_PATH.exists():
        cfg = {'projects': {}}
        save_config(cfg)
        return cfg
    return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))

def save_config(cfg):
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding='utf-8')

class ProjectServer:
    def __init__(self, name, port=None):
        self.name = name
        self.port = port or self._find_free_port()
        self.proc = None

    def _find_free_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 0))
        _, p = s.getsockname()
        s.close()
        return p

    def start(self):
        if self.proc and self.proc.poll() is None:
            return True
        project_path = PROJECTS_DIR / self.name
        if not project_path.exists():
            raise FileNotFoundError(f'Projet {self.name} introuvable')
        # we will launch a tiny static-files server using uvicorn + fastapi simple app
        # create a temporary module file to serve this project
        serve_file = PROJECTS_DIR / self.name / '.pypanel_serve.py'
        # Correction du problème de backslash dans le f-string
        escaped_path = str(project_path).replace('\\', '\\\\')
        serve_code = f"""from fastapi import FastAPI\nfrom fastapi.staticfiles import StaticFiles\napp = FastAPI()\napp.mount('/', StaticFiles(directory='{escaped_path}'), name='static')\n"""
        serve_file.write_text(serve_code, encoding='utf-8')
        cmd = [sys.executable, '-m', 'uvicorn', f"{serve_file.stem}:app", '--host', '127.0.0.1', '--port', str(self.port), '--log-level', 'warning']
        # run inside the project's folder so uvicorn can import the module
        self.proc = subprocess.Popen(cmd, cwd=str(project_path), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        # small wait to allow binding
        time.sleep(0.2)
        return True

    def stop(self, timeout=2):
        if not self.proc:
            return True
        self.proc.terminate()
        try:
            self.proc.wait(timeout=timeout)
        except Exception:
            self.proc.kill()
        self.proc = None
        return True

    def is_running(self):
        return self.proc and self.proc.poll() is None

class ServerManager:
    def __init__(self):
        ensure_projects_dir()
        self._servers = {}
        self.config = load_config()
        # init servers from config
        for name, spec in self.config.get('projects', {}).items():
            self._servers[name] = ProjectServer(name, port=spec.get('port'))

    def list_projects(self):
        ensure_projects_dir()
        return [p.name for p in PROJECTS_DIR.iterdir() if p.is_dir()]

    def get_server(self, name):
        return self._servers.get(name) or None

    def add_project_config(self, name, port=None):
        self.config.setdefault('projects', {})
        self.config['projects'][name] = {'port': port or ProjectServer(name).port}
        save_config(self.config)
        self._servers[name] = ProjectServer(name, port=self.config['projects'][name]['port'])
        return self.config['projects'][name]['port']

    def remove_project_config(self, name):
        if name in self.config.get('projects', {}):
            del self.config['projects'][name]
            save_config(self.config)
        srv = self._servers.pop(name, None)
        if srv:
            srv.stop()

    def start_server(self, name):
        srv = self._servers.get(name)
        if not srv:
            # add default config if missing
            port = self.add_project_config(name)
            srv = self._servers.get(name)
        srv.start()
        return srv.port

    def stop_server(self, name):
        srv = self._servers.get(name)
        if srv:
            srv.stop()

    def start_all(self):
        for name in list(self._servers.keys()):
            try:
                self.start_server(name)
            except Exception:
                pass

    def stop_all(self):
        for name, srv in list(self._servers.items()):
            srv.stop()

# convenience global manager
manager = ServerManager()
