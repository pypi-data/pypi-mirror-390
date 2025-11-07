import os, shutil
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
                             QLabel, QInputDialog, QMessageBox)
from core import server_manager

class ProjectsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.server_manager = server_manager.manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        header = QHBoxLayout()
        header.addWidget(QLabel('<b>Projets</b>'))
        btn_refresh = QPushButton('🔄')
        btn_refresh.clicked.connect(self.refresh_list)
        header.addWidget(btn_refresh)
        layout.addLayout(header)

        self.list = QListWidget()
        layout.addWidget(self.list)

        row = QHBoxLayout()
        btn_start = QPushButton('▶ Démarrer')
        btn_start.clicked.connect(self.start_selected)
        row.addWidget(btn_start)
        btn_stop = QPushButton('⏹ Arrêter')
        btn_stop.clicked.connect(self.stop_selected)
        row.addWidget(btn_stop)
        btn_open = QPushButton('🌐 Ouvrir')
        btn_open.clicked.connect(self.open_selected)
        row.addWidget(btn_open)
        btn_new = QPushButton('➕ Nouveau')
        btn_new.clicked.connect(self.create_project)
        row.addWidget(btn_new)
        btn_delete = QPushButton('🗑️ Supprimer')
        btn_delete.clicked.connect(self.delete_selected)
        row.addWidget(btn_delete)
        btn_port = QPushButton('⚙️ Port')
        btn_port.clicked.connect(self.set_port)
        row.addWidget(btn_port)

        layout.addLayout(row)
        self.setLayout(layout)
        self.refresh_list()

    def refresh_list(self):
        self.list.clear()
        for p in self.server_manager.list_projects():
            self.list.addItem(p)

    def selected(self):
        it = self.list.currentItem()
        return it.text() if it else None

    def start_selected(self):
        name = self.selected()
        if not name: return
        port = self.server_manager.start_server(name)
        QMessageBox.information(self, 'Démarré', f'Projet {name} démarré sur http://127.0.0.1:{port}')

    def stop_selected(self):
        name = self.selected()
        if not name: return
        self.server_manager.stop_server(name)
        QMessageBox.information(self, 'Arrêté', f'Projet {name} arrêté')

    def open_selected(self):
        name = self.selected()
        if not name: return
        port = self.server_manager.config.get('projects', {}).get(name, {}).get('port', None)
        if not port:
            QMessageBox.warning(self, 'Info', 'Le projet n'a pas de port configuré. Démarre-le d'abord.')
            return
        import webbrowser
        webbrowser.open(f'http://127.0.0.1:{port}/index.html')

    def create_project(self):
        name, ok = QInputDialog.getText(self, 'Nouveau projet', 'Nom du projet:')
        if not ok or not name.strip():
            return
        name = name.strip()
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'projects'))
        path = os.path.join(base, name)
        try:
            os.makedirs(path, exist_ok=False)
            with open(os.path.join(path, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(f"<h1>Projet {name}</h1>")
            # add default config
            self.server_manager.add_project_config(name)
            self.refresh_list()
        except Exception as e:
            QMessageBox.critical(self, 'Erreur', str(e))

    def delete_selected(self):
        name = self.selected()
        if not name: return
        confirm = QMessageBox.question(self, 'Confirmer', f'Supprimer {name}?')
        if confirm != QMessageBox.Yes:
            return
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'projects'))
        path = os.path.join(base, name)
        try:
            shutil.rmtree(path)
            self.server_manager.remove_project_config(name)
            self.refresh_list()
        except Exception as e:
            QMessageBox.critical(self, 'Erreur', str(e))

    def set_port(self):
        name = self.selected()
        if not name: return
        port, ok = QInputDialog.getInt(self, 'Port', 'Port HTTP pour le projet:', min=1024, max=65535)
        if not ok: return
        # update config and restart server if running
        cfg = self.server_manager.config
        cfg.setdefault('projects', {})
        cfg['projects'][name] = {'port': port}
        self.server_manager.config = cfg
        self.server_manager.save_config = lambda c: None  # harmless guard
        # persist with manager.save_config function by importing internals
        import json, pathlib
        cfgpath = pathlib.Path(__file__).resolve().parents[2] / 'config.json'
        cfgpath.write_text(json.dumps(cfg, indent=2), encoding='utf-8')
        # restart server
        self.server_manager.stop_server(name)
        self.server_manager._servers[name] = None
        self.server_manager._servers.pop(name, None)
        self.server_manager._servers[name] = server_manager.ProjectServer(name, port=port)
        QMessageBox.information(self, 'Port', f'Port de {name} réglé sur {port}')
