import os, zipfile, tarfile, logging
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

class MultiSiteHTTPRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, sites=None, **kwargs):
        self.sites = sites or []
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path in ["/", ""]:
            self.send_response(302)
            self.send_header('Location', '/test/')
            self.end_headers()
            return
        for prefix, folder, typ, *rest in self.sites:
            if self.path.startswith(prefix):
                status = rest[0] if len(rest) > 0 else "Actif"
                if status == "Inactif":
                    self.send_response(403)
                    self.end_headers()
                    self.wfile.write("Site désactivé".encode("utf-8"))
                    return
                break
        translated_path = self.translate_path(self.path)
        if os.path.isdir(translated_path):
            for homepage in ["index.html", "index.htm", "index.php", "default.html", "default.htm"]:
                homepage_path = os.path.join(translated_path, homepage)
                if os.path.isfile(homepage_path):
                    new_url = self.path.rstrip("/\\") + "/" + homepage
                    self.send_response(302)
                    self.send_header('Location', new_url)
                    self.end_headers()
                    return
        if translated_path.endswith('.php') and os.path.isfile(translated_path):
            self.execute_php(translated_path)
            return
        super().do_GET()

    def execute_php(self, php_file):
        import subprocess
        php_cgi_path = os.path.join(os.getcwd(), "php", "php-cgi.exe")
        try:
            result = subprocess.run([php_cgi_path, php_file], capture_output=True, text=True)
            if '\r\n\r\n' in result.stdout:
                headers, body = result.stdout.split('\r\n\r\n', 1)
            elif '\n\n' in result.stdout:
                headers, body = result.stdout.split('\n\n', 1)
            else:
                headers, body = '', result.stdout
            filtered_headers = []
            for line in headers.splitlines():
                if line.lower().startswith('x-powered-by:'):
                    continue
                if line.lower().startswith('content-type:'):
                    filtered_headers.append('Content-Type: text/html; charset=UTF-8')
                else:
                    filtered_headers.append(line)
            self.send_response(200)
            for header in filtered_headers:
                if ':' in header:
                    key, value = header.split(':', 1)
                    self.send_header(key.strip(), value.strip())
            if not any(h.lower().startswith('content-type:') for h in filtered_headers):
                self.send_header('Content-Type', 'text/html; charset=UTF-8')
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Erreur PHP: {str(e)}".encode("utf-8"))

    def translate_path(self, path):
        for site in sorted(self.sites, key=lambda s: -len(s[0])):
            prefix = site[0]
            folder = site[1]
            # On ignore les autres champs (typ, status...)
            if path.startswith(prefix):
                rel_path = path[len(prefix):]
                return os.path.join(folder, rel_path.lstrip("/\\"))
        return super().translate_path(path)

class DynamicServer:
    def __init__(self, host="127.0.0.1", port=8020, certfile="cert.pem", keyfile="key.pem"):
        self.host = host
        self.port = port
        self.sites = []
        self.log_callback = None
        self.httpd = None
        self.server_thread = None
        logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
        self.logger = logging.getLogger("DynamicServer")

    def set_log_callback(self, callback):
        self.log_callback = callback

    def log(self, message):
        self.logger.info(message)
        if self.log_callback:
            self.log_callback(message)

    def add_static_site(self, prefix, path, status="Actif"):
        # Si le chemin est une archive, déploie automatiquement
        if os.path.isfile(path) and (path.endswith('.zip') or path.endswith('.tar.gz')):
            site_info = self.deploy_archive(path, prefix)
            # Ajoute le site déployé avec le statut demandé
            self.sites.append((site_info['prefix'], site_info['path'], site_info['type'], status))
            self.log(f"Ajout site depuis archive: {site_info['prefix']} -> {site_info['path']} [{status}]")
        else:
            self.sites.append((prefix, path, "static", status))
            self.log(f"Ajout site statique: {prefix} -> {path} [{status}]")

    def add_php_site(self, prefix, path, status="Actif"):
        self.sites.append((prefix, path, "php", status))
        self.log(f"Ajout site PHP: {prefix} -> {path} [{status}]")

    def add_python_app(self, prefix, app_file, status="Actif"):
        self.sites.append((prefix, app_file, "app", status))
        self.log(f"Ajout app Python: {prefix} -> {app_file} [{status}]")

    def deploy_archive(self, archive_path, prefix=None):
        base_name = os.path.splitext(os.path.basename(archive_path))[0]
        target_dir = os.path.join("apps", base_name)
        os.makedirs(target_dir, exist_ok=True)

        if archive_path.endswith(".zip"):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
        elif archive_path.endswith(".tar.gz"):
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                tar_ref.extractall(target_dir)

        if os.path.exists(os.path.join(target_dir, "index.php")):
            site_type = "php"
            self.add_php_site(prefix or f"/{base_name}", target_dir)
        elif os.path.exists(os.path.join(target_dir, "app.py")):
            site_type = "app"
            self.add_python_app(prefix or f"/{base_name}", os.path.join(target_dir, "app.py"))
        elif os.path.exists(os.path.join(target_dir, "index.html")):
            site_type = "static"
            self.add_static_site(prefix or f"/{base_name}", target_dir)
        else:
            site_type = "static"
            self.add_static_site(prefix or f"/{base_name}", target_dir)

        return {"prefix": prefix or f"/{base_name}", "path": target_dir, "type": site_type}

    def start(self):
        if not self.sites:
            test_dir = os.path.join(os.getcwd(), "test_site")
            os.makedirs(test_dir, exist_ok=True)
            index_path = os.path.join(test_dir, "index.html")
            if not os.path.exists(index_path):
                with open(index_path, "w", encoding="utf-8") as f:
                    f.write("""
                    <html><head><title>Site de test</title></head>
                    <body><h1>Bienvenue sur le site de test !</h1></body>
                    </html>
                    """)
            self.add_static_site("/", test_dir)
        handler = lambda *args, **kwargs: MultiSiteHTTPRequestHandler(*args, sites=self.sites, **kwargs)
        self.httpd = HTTPServer((self.host, self.port), handler)
        self.log(f"Serveur HTTP démarré sur http://{self.host}:{self.port} (multi-sites)")
        self.server_thread = threading.Thread(target=self.httpd.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.log("Serveur HTTP arrêté.")
