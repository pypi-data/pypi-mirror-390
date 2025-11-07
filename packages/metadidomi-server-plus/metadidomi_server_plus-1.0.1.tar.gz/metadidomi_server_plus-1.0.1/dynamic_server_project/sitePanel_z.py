import sys
import os
import sqlite3
import configparser
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFileDialog, QListWidget, QMessageBox, 
                             QTextEdit, QTabWidget, QGroupBox, QLabel, QLineEdit,
                             QListWidgetItem, QSplitter, QProgressBar, QTreeWidget,
                             QTreeWidgetItem, QHeaderView, QMenu, QAction, QInputDialog,
                             QTableWidget, QTableWidgetItem, QComboBox, QCheckBox,
                             QSpinBox, QFormLayout, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QColor
import threading
import time
from datetime import datetime

# Ajout du dossier site-packages local pour python-embed-amd64
sys.path.insert(0, os.path.join(os.getcwd(), 'python-embed-amd64', 'Lib', 'site-packages'))

# Importez votre serveur existant
from server_core import DynamicServer

class DatabaseManager:
    def __init__(self):
        self.databases_dir = "databases"
        os.makedirs(self.databases_dir, exist_ok=True)
    
    def create_database(self, db_name):
        """Crée une nouvelle base de données SQLite"""
        db_path = os.path.join(self.databases_dir, f"{db_name}.db")
        conn = sqlite3.connect(db_path)
        conn.close()
        return db_path
    
    def delete_database(self, db_name):
        """Supprime une base de données"""
        db_path = os.path.join(self.databases_dir, f"{db_name}.db")
        if os.path.exists(db_path):
            os.remove(db_path)
            return True
        return False
    
    def execute_query(self, db_name, query):
        """Exécute une requête SQL"""
        db_path = os.path.join(self.databases_dir, f"{db_name}.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(query)
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                conn.close()
                return columns, results
            else:
                conn.commit()
                conn.close()
                return None, f"Query executed successfully. Rows affected: {cursor.rowcount}"
        except Exception as e:
            conn.close()
            raise e
    
    def get_database_tables(self, db_name):
        """Récupère la liste des tables d'une base de données"""
        db_path = os.path.join(self.databases_dir, f"{db_name}.db")
        if not os.path.exists(db_path):
            return []
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        conn.close()
        return tables
    
    def get_table_structure(self, db_name, table_name):
        """Récupère la structure d'une table"""
        db_path = os.path.join(self.databases_dir, f"{db_name}.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        structure = cursor.fetchall()
        conn.close()
        return structure
    
    def get_table_data(self, db_name, table_name, limit=100):
        """Récupère les données d'une table"""
        db_path = os.path.join(self.databases_dir, f"{db_name}.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        columns = [description[0] for description in cursor.description]
        data = cursor.fetchall()
        conn.close()
        return columns, data

class PHPConfigDialog(QDialog):
    def __init__(self, parent=None, current_config=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration PHP")
        self.setModal(True)
        self.resize(500, 600)
        self.init_ui()
        self.current_config = current_config
        self.load_current_config()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Configuration de base
        basic_group = QGroupBox("Configuration de base")
        basic_layout = QFormLayout(basic_group)
        
        self.memory_limit = QLineEdit("128M")
        basic_layout.addRow("Memory Limit:", self.memory_limit)
        
        self.max_execution_time = QSpinBox()
        self.max_execution_time.setRange(0, 300)
        self.max_execution_time.setValue(30)
        basic_layout.addRow("Max Execution Time (s):", self.max_execution_time)
        
        self.upload_max_filesize = QLineEdit("2M")
        basic_layout.addRow("Upload Max Filesize:", self.upload_max_filesize)
        
        self.post_max_size = QLineEdit("8M")
        basic_layout.addRow("Post Max Size:", self.post_max_size)
        
        layout.addWidget(basic_group)
        
        # Affichage des erreurs
        error_group = QGroupBox("Affichage des erreurs")
        error_layout = QVBoxLayout(error_group)
        
        self.display_errors = QCheckBox("Afficher les erreurs")
        self.display_errors.setChecked(True)
        error_layout.addWidget(self.display_errors)
        
        self.error_reporting = QComboBox()
        self.error_reporting.addItems([
            "E_ALL & ~E_NOTICE",
            "E_ALL",
            "E_ALL & ~E_DEPRECATED",
            "E_ERROR | E_WARNING | E_PARSE"
        ])
        error_layout.addWidget(QLabel("Niveau de rapport d'erreurs:"))
        error_layout.addWidget(self.error_reporting)
        
        layout.addWidget(error_group)
        
        # Extensions
        extensions_group = QGroupBox("Extensions PHP")
        extensions_layout = QVBoxLayout(extensions_group)
        
        self.ext_gd = QCheckBox("GD (Manipulation d'images)")
        self.ext_gd.setChecked(True)
        extensions_layout.addWidget(self.ext_gd)
        
        self.ext_mysqli = QCheckBox("MySQLi (Bases de données MySQL)")
        self.ext_mysqli.setChecked(True)
        extensions_layout.addWidget(self.ext_mysqli)
        
        self.ext_curl = QCheckBox("cURL (Requêtes HTTP)")
        self.ext_curl.setChecked(True)
        extensions_layout.addWidget(self.ext_curl)
        
        self.ext_json = QCheckBox("JSON")
        self.ext_json.setChecked(True)
        extensions_layout.addWidget(self.ext_json)
        
        layout.addWidget(extensions_group)
        
        # Boutons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_current_config(self):
        if self.current_config:
            self.memory_limit.setText(self.current_config.get('memory_limit', '128M'))
            self.max_execution_time.setValue(int(self.current_config.get('max_execution_time', 30)))
            self.upload_max_filesize.setText(self.current_config.get('upload_max_filesize', '2M'))
            self.post_max_size.setText(self.current_config.get('post_max_size', '8M'))
            self.display_errors.setChecked(self.current_config.get('display_errors', 'On') in ['On', True, 'True'])
            idx = self.error_reporting.findText(self.current_config.get('error_reporting', 'E_ALL & ~E_NOTICE'))
            if idx >= 0:
                self.error_reporting.setCurrentIndex(idx)
            # Extensions
            extensions = self.current_config.get('extensions', {})
            self.ext_gd.setChecked(extensions.get('gd', True))
            self.ext_mysqli.setChecked(extensions.get('mysqli', True))
            self.ext_curl.setChecked(extensions.get('curl', True))
            self.ext_json.setChecked(extensions.get('json', True))
    
    def get_config(self):
        """Retourne la configuration PHP sous forme de dictionnaire"""
        return {
            'memory_limit': self.memory_limit.text(),
            'max_execution_time': self.max_execution_time.value(),
            'upload_max_filesize': self.upload_max_filesize.text(),
            'post_max_size': self.post_max_size.text(),
            'display_errors': self.display_errors.isChecked(),
            'error_reporting': self.error_reporting.currentText(),
            'extensions': {
                'gd': self.ext_gd.isChecked(),
                'mysqli': self.ext_mysqli.isChecked(),
                'curl': self.ext_curl.isChecked(),
                'json': self.ext_json.isChecked()
            }
        }

class SQLQueryDialog(QDialog):
    def __init__(self, db_manager, db_name, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.db_name = db_name
        self.setWindowTitle(f"Exécuter une requête SQL - {db_name}")
        self.setModal(True)
        self.resize(700, 500)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Éditeur de requête
        layout.addWidget(QLabel("Requête SQL:"))
        self.query_edit = QTextEdit()
        self.query_edit.setPlaceholderText("Entrez votre requête SQL ici...")
        self.query_edit.setFont(QFont("Courier", 10))
        layout.addWidget(self.query_edit)
        
        # Boutons d'exécution
        button_layout = QHBoxLayout()
        
        self.execute_btn = QPushButton("Exécuter")
        self.execute_btn.clicked.connect(self.execute_query)
        button_layout.addWidget(self.execute_btn)
        
        self.clear_btn = QPushButton("Effacer")
        self.clear_btn.clicked.connect(self.query_edit.clear)
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Résultats
        layout.addWidget(QLabel("Résultats:"))
        self.results_table = QTableWidget()
        layout.addWidget(self.results_table)
        
        # Messages
        self.message_label = QLabel()
        self.message_label.setStyleSheet("padding: 5px;")
        layout.addWidget(self.message_label)
    
    def execute_query(self):
        query = self.query_edit.toPlainText().strip()
        if not query:
            self.show_message("❌ Veuillez entrer une requête SQL", "red")
            return
        
        try:
            columns, results = self.db_manager.execute_query(self.db_name, query)
            
            if columns:  # Requête SELECT
                self.display_results(columns, results)
                self.show_message(f"✅ Requête exécutée avec succès - {len(results)} ligne(s) retournée(s)", "green")
            else:  # Autre type de requête
                self.results_table.setRowCount(0)
                self.results_table.setColumnCount(0)
                self.show_message(f"✅ {results}", "green")
                
        except Exception as e:
            self.show_message(f"❌ Erreur SQL: {str(e)}", "red")
    
    def display_results(self, columns, data):
        self.results_table.setRowCount(len(data))
        self.results_table.setColumnCount(len(columns))
        self.results_table.setHorizontalHeaderLabels(columns)
        
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data) if cell_data is not None else "NULL")
                self.results_table.setItem(row_idx, col_idx, item)
    
    def show_message(self, message, color):
        self.message_label.setText(message)
        self.message_label.setStyleSheet(f"color: {color}; padding: 5px; font-weight: bold;")

class ServerThread(QThread):
    log_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)
    
    def __init__(self, server):
        super().__init__()
        self.server = server
        self.running = False
        
    def run(self):
        self.running = True
        self.status_signal.emit("🟢 Serveur démarré")
        try:
            self.server.start()
        except Exception as e:
            self.log_signal.emit(f"❌ Erreur serveur: {str(e)}")
            self.status_signal.emit("🔴 Erreur")
        finally:
            self.running = False
            
    def stop(self):
        self.running = False
        if self.server:
            self.server.stop()
        self.status_signal.emit("🔴 Serveur arrêté")

class SitePanel(QWidget):
    def __init__(self):
        super().__init__()
        self.server = DynamicServer()
        self.db_manager = DatabaseManager()
        self.server_thread = None
        self.php_config = self.load_php_config()
        self.init_ui()
        self.add_default_test_site()  # Ajoute le site de test par défaut
        self.load_existing_sites()
        self.load_databases()

    def closeEvent(self, event):
        event.accept()

    def add_default_test_site(self):
        # Crée un dossier de test s'il n'existe pas
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
        prefix = "/test"
        self.server.add_static_site(prefix, test_dir)
        self.add_site_to_tree(prefix, "Statique", test_dir, "Actif")
        self.log(f"✅ Site de test ajouté: {prefix} -> {test_dir}")
        # Ajout d'une base de données pour le site de test
        db_name = "test_site"
        db_path = os.path.join("databases", f"{db_name}.db")
        if not os.path.exists("databases"):
            os.makedirs("databases")
        if not os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE IF NOT EXISTS demo (id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT)")
            conn.execute("INSERT INTO demo (message) VALUES ('Bienvenue dans la base de test !')")
            conn.commit()
            conn.close()
            self.log(f"🗄️ Base de données test_site créée pour le site de test.")

    def init_ui(self):
        self.setWindowTitle("sitePanel Manager")
        self.setGeometry(100, 100, 1200, 600)
        
        # Layout principal
        main_layout = QHBoxLayout(self)
        
        # Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Zone de contenu principale avec onglets
        self.tabs = QTabWidget()
        self.setup_dashboard_tab()
        self.setup_sites_tab()
        self.setup_files_tab()
        self.setup_databases_tab()
        self.setup_logs_tab()
        self.setup_settings_tab()
        
        main_layout.addWidget(self.tabs, 1)
        
    def create_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: white;
                font-weight: bold;
            }
            QPushButton {
                background-color: #34495e;
                color: white;
                border: none;
                padding: 10px;
                text-align: left;
                border-radius: 5px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        layout = QVBoxLayout(sidebar)
        
        # Logo/Header
        header = QLabel("Bienvenue !")
        header.setStyleSheet("font-size: 18px; padding: 20px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Boutons de navigation
        nav_buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("🌐 Sites Web", self.show_sites),
            ("📁 Gestion Fichiers", self.show_files),
            ("🗄️ Bases de données", self.show_databases),
            ("📋 Logs", self.show_logs),
            ("⚙️ Paramètres", self.show_settings),
        ]
        
        for text, slot in nav_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            layout.addWidget(btn)
        
        # Status du serveur
        layout.addStretch()
        status_group = QGroupBox("Status Serveur")
        status_layout = QVBoxLayout(status_group)
        
        self.server_status = QLabel("🔴 Arrêté")
        self.server_status.setStyleSheet("font-size: 14px; padding: 10px;")
        status_layout.addWidget(self.server_status)
        
        # Deux boutons distincts
        self.start_btn = QPushButton("Démarrer le serveur")
        self.start_btn.clicked.connect(self.start_server)
        status_layout.addWidget(self.start_btn)
        self.stop_btn = QPushButton("Arrêter le serveur")
        self.stop_btn.clicked.connect(self.stop_server)
        status_layout.addWidget(self.stop_btn)
        self.update_server_buttons()
        
        layout.addWidget(status_group)
        
        return sidebar

    def update_server_buttons(self):
        running = False
        if self.server_thread is not None:
            try:
                running = self.server_thread.isRunning()
            except Exception:
                running = False
        if hasattr(self, 'start_btn') and self.start_btn is not None:
            self.start_btn.setEnabled(not running)
            self.start_btn.setVisible(not running)
        if hasattr(self, 'stop_btn') and self.stop_btn is not None:
            self.stop_btn.setEnabled(running)
            self.stop_btn.setVisible(running)

    def start_server(self):
        if not (self.server_thread and self.server_thread.isRunning()):
            self.toggle_server()
        self.update_server_buttons()

    def stop_server(self):
        if self.server_thread and self.server_thread.isRunning():
            self.toggle_server()
        self.update_server_buttons()

    def setup_dashboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        stats_group = QGroupBox("Statistiques du serveur")
        stats_layout = QHBoxLayout(stats_group)

        # Calcul des vraies stats
        sites_actifs = 0
        espace_utilise = "0 MB"
        requetes = getattr(self.server, "request_count", 0)
        cpu = self.get_cpu_usage()
        # On ne peut pas compter les sites actifs si la liste n'est pas encore créée
        if hasattr(self, 'sites_tree'):
            sites_actifs = sum(1 for i in range(self.sites_tree.topLevelItemCount()) if self.sites_tree.topLevelItem(i).text(4) == "Actif")
            espace_utilise = self.get_total_disk_usage()

        stats = [
            ("Sites actifs", str(sites_actifs)),
            ("Espace utilisé", espace_utilise),
            ("Requêtes aujourd'hui", str(requetes)),
            ("CPU", cpu)
        ]

        for label, value in stats:
            stat_widget = QWidget()
            stat_layout = QVBoxLayout(stat_widget)
            stat_layout.addWidget(QLabel(label))
            stat_layout.addWidget(QLabel(value))
            stats_layout.addWidget(stat_widget)

        layout.addWidget(stats_group)
        # Actions rapides
        quick_actions = QGroupBox("Actions rapides")
        actions_layout = QHBoxLayout(quick_actions)
        
        actions = [
            ("➕ Nouveau Site", self.add_static_site),
            ("📤 Upload Archive", self.upload_and_deploy),
            ("🔧 PHP Config", self.show_php_config),
            ("🛡️ Sécurité", self.show_security)
        ]
        
        for text, slot in actions:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            actions_layout.addWidget(btn)
        
        layout.addWidget(quick_actions)
        layout.addStretch()
        
        self.tabs.addTab(tab, "📊 Dashboard")

    def get_total_disk_usage(self):
        total = 0
        for i in range(self.sites_tree.topLevelItemCount()):
            path = self.sites_tree.topLevelItem(i).text(2)
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for f in files:
                        fp = os.path.join(root, f)
                        if os.path.isfile(fp):
                            total += os.path.getsize(fp)
        mb = total / (1024 * 1024)
        return f"{mb:.2f} MB"

    def get_cpu_usage(self):
        try:
            import psutil
            return f"{psutil.cpu_percent()}%"
        except:
            return "N/A"

    def setup_sites_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Barre d'outils sites
        toolbar = QHBoxLayout()
        
        self.add_static_btn = QPushButton("➕ Site Statique")
        self.add_static_btn.clicked.connect(self.add_static_site)
        toolbar.addWidget(self.add_static_btn)
        
        self.upload_btn = QPushButton("📤 Upload Archive")
        self.upload_btn.clicked.connect(self.upload_and_deploy)
        toolbar.addWidget(self.upload_btn)
        
        self.delete_site_btn = QPushButton("🗑️ Supprimer")
        self.delete_site_btn.clicked.connect(self.delete_site)
        toolbar.addWidget(self.delete_site_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Liste des sites avec plus d'informations
        self.sites_tree = QTreeWidget()
        self.sites_tree.setHeaderLabels(["Nom", "Type", "Chemin", "URL", "Statut"])
        self.sites_tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.sites_tree.itemDoubleClicked.connect(self.edit_site)
        self.sites_tree.currentItemChanged.connect(self.on_site_selected)
        layout.addWidget(self.sites_tree)
        
        self.tabs.addTab(tab, "🌐 Sites Web")
    
    def setup_files_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Navigation fichiers
        nav_layout = QHBoxLayout()
        self.current_path = QLineEdit()
        # Par défaut, chemin du site de test
        test_dir = os.path.join(os.getcwd(), "test_site")
        self.current_path.setText(test_dir)
        nav_layout.addWidget(QLabel("Chemin:"))
        nav_layout.addWidget(self.current_path)
        
        self.refresh_files_btn = QPushButton("🔄")
        self.refresh_files_btn.clicked.connect(self.refresh_file_browser)
        nav_layout.addWidget(self.refresh_files_btn)
        
        layout.addLayout(nav_layout)
        
        # Browser de fichiers
        splitter = QSplitter(Qt.Horizontal)
        
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Nom", "Taille", "Type", "Modifié"])
        self.file_tree.itemDoubleClicked.connect(self.on_file_double_click)
        splitter.addWidget(self.file_tree)
        
        # Preview/éditeur
        self.file_preview = QTextEdit()
        self.file_preview.setReadOnly(True)
        splitter.addWidget(self.file_preview)
        
        splitter.setSizes([400, 400])
        layout.addWidget(splitter)
        
        self.tabs.addTab(tab, "📁 Fichiers")
        self.refresh_file_browser()
    
    def setup_databases_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        engine_group = QGroupBox("Moteur de base de données")
        engine_layout = QFormLayout(engine_group)
        self.db_engine_combo = QComboBox()
        self.db_engine_combo.addItems(["SQLite"]) # MySQL supprimé
        self.db_engine_combo.currentTextChanged.connect(self.on_db_engine_changed)
        engine_layout.addRow("Moteur:", self.db_engine_combo)
        layout.addWidget(engine_group)
        db_toolbar = QHBoxLayout()
        self.create_db_btn = QPushButton("➕ Nouvelle Base")
        self.create_db_btn.clicked.connect(self.create_database)
        db_toolbar.addWidget(self.create_db_btn)
        self.delete_db_btn = QPushButton("🗑️ Supprimer")
        self.delete_db_btn.clicked.connect(self.delete_database)
        db_toolbar.addWidget(self.delete_db_btn)
        self.query_btn = QPushButton("🔍 Exécuter Requête")
        self.query_btn.clicked.connect(self.execute_sql_query)
        db_toolbar.addWidget(self.query_btn)
        db_toolbar.addStretch()
        layout.addLayout(db_toolbar)
        splitter = QSplitter(Qt.Horizontal)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("Bases de données:"))
        self.databases_list = QListWidget()
        self.databases_list.currentItemChanged.connect(self.on_database_selected)
        left_layout.addWidget(self.databases_list)
        left_layout.addWidget(QLabel("Tables:"))
        self.tables_list = QListWidget()
        self.tables_list.itemDoubleClicked.connect(self.on_table_double_click)
        left_layout.addWidget(self.tables_list)
        splitter.addWidget(left_panel)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.db_tabs = QTabWidget()
        self.structure_table = QTableWidget()
        self.db_tabs.addTab(self.structure_table, "Structure")
        self.data_table = QTableWidget()
        self.db_tabs.addTab(self.data_table, "Données")
        right_layout.addWidget(self.db_tabs)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 500])
        layout.addWidget(splitter)
        self.tabs.addTab(tab, "🗄️ Bases de données")
        self.on_db_engine_changed(self.db_engine_combo.currentText())

    def on_db_engine_changed(self, engine):
        self.db_manager = DatabaseManager()
        self.load_databases()

    def load_databases(self):
        self.databases_list.clear()
        databases_dir = "databases"
        if os.path.exists(databases_dir):
            for file in os.listdir(databases_dir):
                if file.endswith('.db'):
                    self.databases_list.addItem(file[:-3])

    def create_database(self):
        name, ok = QInputDialog.getText(self, "Nouvelle base de données", "Nom de la base de données:")
        if ok and name:
            try:
                self.db_manager.create_database(name)
                self.load_databases()
                self.log(f"🗄️ Base de données créée: {name}")
                QMessageBox.information(self, "Succès", f"Base de données '{name}' créée avec succès!")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la création: {str(e)}")

    def delete_database(self):
        current_item = self.databases_list.currentItem()
        if current_item:
            db_name = current_item.text()
            reply = QMessageBox.question(self, "Confirmation", f"Supprimer la base de données '{db_name}'?")
            if reply == QMessageBox.Yes:
                try:
                    if self.db_manager.delete_database(db_name):
                        self.load_databases()
                        self.tables_list.clear()
                        self.structure_table.setRowCount(0)
                        self.data_table.setRowCount(0)
                        self.log(f"🗑️ Base de données supprimée: {db_name}")
                    else:
                        QMessageBox.warning(self, "Erreur", "Base de données non trouvée")
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {str(e)}")

    def on_database_selected(self, current, previous):
        if current:
            db_name = current.text()
            tables = self.db_manager.get_database_tables(db_name)
            self.tables_list.clear()
            self.tables_list.addItems(tables)

    def on_table_double_click(self, item):
        db_item = self.databases_list.currentItem()
        if db_item and item:
            db_name = db_item.text()
            table_name = item.text()
            self.show_table_structure(db_name, table_name)
            self.show_table_data(db_name, table_name)

    def show_table_structure(self, db_name, table_name):
        structure = self.db_manager.get_table_structure(db_name, table_name)
        self.structure_table.setRowCount(len(structure))
        self.structure_table.setColumnCount(6)
        self.structure_table.setHorizontalHeaderLabels([
            "CID", "Nom", "Type", "Not Null", "Valeur par défaut", "PK"
        ])
        for row_idx, column in enumerate(structure):
            for col_idx in range(6):
                item = QTableWidgetItem(str(column[col_idx]) if column[col_idx] is not None else "")
                self.structure_table.setItem(row_idx, col_idx, item)

    def show_table_data(self, db_name, table_name):
        columns, data = self.db_manager.get_table_data(db_name, table_name)
        self.data_table.setRowCount(len(data))
        self.data_table.setColumnCount(len(columns))
        self.data_table.setHorizontalHeaderLabels(columns)
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data) if cell_data is not None else "NULL")
                self.data_table.setItem(row_idx, col_idx, item)

    def execute_sql_query(self):
        current_item = self.databases_list.currentItem()
        if current_item:
            db_name = current_item.text()
            dialog = SQLQueryDialog(self.db_manager, db_name, self)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une base de données")
    
    def setup_logs_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Contrôles logs
        log_controls = QHBoxLayout()
        
        self.clear_logs_btn = QPushButton("Effacer les logs")
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        log_controls.addWidget(self.clear_logs_btn)
        
        self.save_logs_btn = QPushButton("Sauvegarder logs")
        self.save_logs_btn.clicked.connect(self.save_logs)
        log_controls.addWidget(self.save_logs_btn)
        
        log_controls.addStretch()
        layout.addLayout(log_controls)
        
        # Console de logs
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setFont(QFont("Courier", 10))
        layout.addWidget(self.log_console)
        
        self.tabs.addTab(tab, "📋 Logs")
    
    def setup_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Configuration serveur
        server_config = QGroupBox("Configuration Serveur")
        config_layout = QVBoxLayout(server_config)
        
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        self.port_input = QLineEdit("8000")
        port_layout.addWidget(self.port_input)
        config_layout.addLayout(port_layout)
        
        # Configuration PHP
        php_config_btn = QPushButton("🔧 Configuration PHP")
        php_config_btn.clicked.connect(self.show_php_config)
        config_layout.addWidget(php_config_btn)
        
        layout.addWidget(server_config)
        
        # Affichage configuration PHP actuelle
        current_php_group = QGroupBox("Configuration PHP Actuelle")
        php_layout = QVBoxLayout(current_php_group)
        
        self.php_config_display = QTextEdit()
        self.php_config_display.setReadOnly(True)
        self.php_config_display.setMaximumHeight(200)
        php_layout.addWidget(self.php_config_display)
        
        layout.addWidget(current_php_group)
        self.update_php_config_display()
        
        layout.addStretch()
        
        self.tabs.addTab(tab, "⚙️ Paramètres")
    
    def show_dashboard(self):
        self.tabs.setCurrentIndex(0)
    
    def show_sites(self):
        self.tabs.setCurrentIndex(1)
    
    def show_files(self):
        self.tabs.setCurrentIndex(2)
    
    def show_databases(self):
        self.tabs.setCurrentIndex(3)
    
    def show_logs(self):
        self.tabs.setCurrentIndex(4)
    
    def show_settings(self):
        self.tabs.setCurrentIndex(5)
    
    # Méthodes pour la configuration PHP
    def show_php_config(self):
        """Affiche la dialog de configuration PHP"""
        dialog = PHPConfigDialog(self, current_config=self.php_config)
        if dialog.exec_() == QDialog.Accepted:
            self.php_config = dialog.get_config()
            self.save_php_config()
            self.update_php_config_display()
            self.log("🔧 Configuration PHP mise à jour")
            QMessageBox.information(self, "Succès", "Configuration PHP sauvegardée!")
    
    def load_php_config(self):
        """Charge la configuration PHP depuis le fichier"""
        config_file = "php_config.ini"
        config = configparser.ConfigParser()
        default_config = {
            'memory_limit': '128M',
            'max_execution_time': '30',
            'upload_max_filesize': '2M',
            'post_max_size': '8M',
            'display_errors': 'On',
            'error_reporting': 'E_ALL & ~E_NOTICE',
            'extensions': {
                'gd': True,
                'mysqli': True,
                'curl': True,
                'json': True
            }
        }
        if os.path.exists(config_file):
            config.read(config_file)
            if 'PHP' in config:
                cfg = dict(config['PHP'])
                # Reconstruire les extensions
                extensions = {}
                for ext in ['gd', 'mysqli', 'curl', 'json']:
                    extensions[ext] = cfg.get(f'ext_{ext}', 'True') in ['True', 'true', '1', 'On']
                cfg['extensions'] = extensions
                return cfg
        return default_config
    
    def save_php_config(self):
        """Sauvegarde la configuration PHP dans un fichier"""
        config = configparser.ConfigParser()
        # Extensions doivent être converties en chaîne
        php_cfg = self.php_config.copy()
        if 'extensions' in php_cfg:
            for ext, val in php_cfg['extensions'].items():
                php_cfg[f'ext_{ext}'] = str(val)
            del php_cfg['extensions']
        config['PHP'] = {k: str(v) for k, v in php_cfg.items()}
        with open('php_config.ini', 'w') as configfile:
            config.write(configfile)
    
    def update_php_config_display(self):
        """Met à jour l'affichage de la configuration PHP"""
        display_text = ""
        for key, value in self.php_config.items():
            display_text += f"{key}: {value}\n"
        self.php_config_display.setPlainText(display_text)
    
    # Les autres méthodes restent inchangées...
    def add_static_site(self):
        folder = QFileDialog.getExistingDirectory(self, "Choisir un dossier statique")
        if folder:
            # Si le dossier sélectionné est une archive, on l'extrait automatiquement
            if folder.endswith('.zip') or folder.endswith('.tar.gz') or folder.endswith('.tar'):
                base_name = os.path.splitext(os.path.basename(folder))[0]
                target_dir = os.path.join("apps", base_name)
                os.makedirs(target_dir, exist_ok=True)
                if folder.endswith(".zip"):
                    import zipfile
                    with zipfile.ZipFile(folder, 'r') as zip_ref:
                        zip_ref.extractall(target_dir)
                elif folder.endswith(".tar.gz"):
                    import tarfile
                    with tarfile.open(folder, 'r:gz') as tar_ref:
                        tar_ref.extractall(target_dir)
                elif folder.endswith(".tar"):
                    import tarfile
                    with tarfile.open(folder, 'r:') as tar_ref:
                        tar_ref.extractall(target_dir)
                folder = target_dir
            site_name = os.path.basename(folder)
            prefix, ok = QInputDialog.getText(self, "Prefix du site", "Entrez le prefix (ex: /monsite):", text=f"/{site_name}")
            if ok and prefix:
                homepage_files = ["index.html", "index.htm", "index.php", "default.html", "default.htm"]
                found = [f for f in homepage_files if os.path.isfile(os.path.join(folder, f))]
                homepage = None
                if found:
                    if len(found) == 1:
                        homepage = found[0]
                    else:
                        homepage, ok2 = QInputDialog.getItem(self, "Page d'accueil", "Choisissez la page d'accueil :", found, 0, False)
                        if not ok2:
                            homepage = found[0]
                try:
                    self.server.add_static_site(prefix, folder)
                    self.add_site_to_tree(prefix, "Statique", folder, "Actif", homepage)
                    self.log(f"✅ Site statique ajouté: {prefix} -> {folder} (accueil: {homepage if homepage else 'aucun'})")
                except Exception as e:
                    self.log(f"❌ Erreur: {str(e)}")

    def add_site_to_tree(self, name, site_type, path, status, homepage=None):
        homepage_files = ["index.html", "index.htm", "index.php", "default.html", "default.htm"]
        if homepage is None:
            homepage = None
            for fname in homepage_files:
                fpath = os.path.join(path, fname)
                if os.path.isfile(fpath):
                    homepage = fname
                    break
        if homepage:
            url = f"http://localhost:8020{name}/{homepage}" if not name.endswith("/") else f"http://localhost:8020{name}{homepage}"
        else:
            url = f"http://localhost:8020{name}"
        item = QTreeWidgetItem([name, site_type, path, url, status])
        font = QFont()
        font.setUnderline(True)
        item.setFont(3, font)
        color = QColor("#3498db")
        item.setForeground(3, color)
        self.sites_tree.addTopLevelItem(item)
        self.sites_tree.setItemWidget(item, 3, self._make_url_label(url, status))

    def upload_and_deploy(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Choisir une archive", "", 
                                                 "Archives (*.zip *.tar.gz *.tar)")
        if file_path:
            try:
                self.log(f"📤 Déploiement de l'archive: {file_path}")
                site_info = self.server.deploy_archive(file_path)
                self.add_site_to_tree(site_info['prefix'], site_info['type'], 
                                    site_info['path'], "Actif")
                self.log(f"✅ Site déployé: {site_info['prefix']} ({site_info['type']})")
                QMessageBox.information(self, "Succès", 
                                      f"Site {site_info['type']} déployé sur {site_info['prefix']}")
            except Exception as e:
                self.log(f"❌ Erreur déploiement: {str(e)}")
                QMessageBox.critical(self, "Erreur", str(e))
    
    def delete_site(self):
        current_item = self.sites_tree.currentItem()
        if current_item:
            site_name = current_item.text(0)
            # Empêche la suppression du site de test
            if (site_name == "/test"):
                QMessageBox.warning(self, "Interdit", "Le site de test ne peut pas être supprimé.")
                return
            reply = QMessageBox.question(self, "Confirmation", 
                                       f"Supprimer le site {site_name}?")
            if reply == QMessageBox.Yes:
                self.sites_tree.takeTopLevelItem(self.sites_tree.indexOfTopLevelItem(current_item))
                self.log(f"🗑️ Site supprimé: {site_name}")
    
    def edit_site(self, item, column):
        # Édition des propriétés du site
        site_name = item.text(0)
        new_name, ok = QInputDialog.getText(self, "Modifier le site", 
                                          "Nouveau nom:", text=site_name)
        if ok:
            item.setText(0, new_name)
            self.log(f"✏️ Site modifié: {site_name} -> {new_name}")
    
    def refresh_file_browser(self):
        self.file_tree.clear()
        # Affiche les fichiers du site sélectionné
        current_item = self.sites_tree.currentItem()
        if current_item:
            site_path = current_item.text(2)  # Chemin du site
        else:
            site_path = self.current_path.text()
        if os.path.exists(site_path):
            for item in os.listdir(site_path):
                full_path = os.path.join(site_path, item)
                if os.path.isdir(full_path):
                    tree_item = QTreeWidgetItem([item, "", "Dossier", ""])
                    tree_item.setData(0, Qt.UserRole, full_path)
                    self.file_tree.addTopLevelItem(tree_item)
                else:
                    size = os.path.getsize(full_path)
                    modified = datetime.fromtimestamp(os.path.getmtime(full_path))
                    tree_item = QTreeWidgetItem([item, f"{size} bytes", "Fichier", 
                                               modified.strftime("%Y-%m-%d %H:%M")])
                    tree_item.setData(0, Qt.UserRole, full_path)
                    self.file_tree.addTopLevelItem(tree_item)

    def on_file_double_click(self, item, column):
        path = item.data(0, Qt.UserRole)
        if os.path.isdir(path):
            self.current_path.setText(path)
            self.refresh_file_browser()
        else:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.file_preview.setPlainText(content)
            except:
                self.file_preview.setPlainText("⚠️ Impossible de lire le fichier")
    
    def toggle_server(self):
        if self.server_thread and self.server_thread.isRunning():
            self.server_thread.stop()
            self.server_thread.wait()
            self.server_thread = None
        else:
            self.server_thread = ServerThread(self.server)
            self.server_thread.log_signal.connect(self.log)
            self.server_thread.status_signal.connect(self.update_server_status)
            self.server_thread.start()
    
    def update_server_status(self, status):
        self.server_status.setText(status)
        self.update_server_buttons()
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_console.append(f"[{timestamp}] {message}")
    
    def clear_logs(self):
        self.log_console.clear()
    
    def save_logs(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Sauvegarder les logs", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.log_console.toPlainText())
            self.log(f"💾 Logs sauvegardés: {file_path}")
    
    def load_existing_sites(self):
        # Chargez les sites existants depuis votre serveur
        # Cette méthode dépend de l'implémentation de votre DynamicServer
        pass
    
    def show_security(self):
        QMessageBox.information(self, "Sécurité", "Paramètres de sécurité (à implémenter)")

    def on_site_selected(self, current, previous):
        if current:
            site_path = current.text(2)
            self.current_path.setText(site_path)
            self.refresh_file_browser()
        if current:
            url = current.text(3)
            status = current.text(4)
            self.sites_tree.setItemWidget(current, 3, self._make_url_label(url, status))

    def _make_url_label(self, url, status=None):
        # Si le site est désactivé, le lien n'est pas cliquable
        label = QLabel()
        if (status == "Inactif"):
            label.setText(f'{url} (désactivé)')
            label.setStyleSheet('color: #aaa;')
            label.setTextInteractionFlags(Qt.NoTextInteraction)
        else:
            label.setText(f'<a href="{url}">{url}</a>')
            label.setOpenExternalLinks(True)
            label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        return label

    def toggle_site_status(self, item):
        current_status = item.text(4)
        new_status = "Inactif" if current_status == "Actif" else "Actif"
        item.setText(4, new_status)
        url = item.text(3)
        self.sites_tree.setItemWidget(item, 3, self._make_url_label(url, new_status))
        self.log(f"🔄 Statut du site '{item.text(0)}' changé en {new_status}")

    def contextMenuEvent(self, event):
        # Menu contextuel pour la liste des sites
        item = self.sites_tree.itemAt(self.sites_tree.viewport().mapFromGlobal(event.globalPos()))
        if item:
            menu = QMenu(self)
            change_homepage_action = QAction("Changer la page d'accueil", self)
            change_homepage_action.triggered.connect(lambda: self.change_homepage_for_site(item))
            menu.addAction(change_homepage_action)

            # Option Activer/Désactiver le site
            current_status = item.text(4)
            toggle_status_action = QAction(
                "Désactiver le site" if current_status == "Actif" else "Activer le site", self)
            toggle_status_action.triggered.connect(lambda: self.toggle_site_status(item))
            menu.addAction(toggle_status_action)

            # Option Paramétrer dynamiquement
            param_action = QAction("Paramétrer dynamiquement", self)
            param_action.triggered.connect(lambda: self.dynamic_site_settings(item))
            menu.addAction(param_action)

            menu.exec_(event.globalPos())

    def dynamic_site_settings(self, item):
        # Permet de modifier dynamiquement le nom et le type du site
        site_name = item.text(0)
        site_type = item.text(1)
        new_name, ok1 = QInputDialog.getText(self, "Paramétrage du site", "Nom du site:", text=site_name)
        if ok1 and new_name:
            item.setText(0, new_name)
        new_type, ok2 = QInputDialog.getText(self, "Paramétrage du site", "Type du site:", text=site_type)
        if ok2 and new_type:
            item.setText(1, new_type)
        self.log(f"⚙️ Paramètres modifiés pour le site '{site_name}'")

    def change_homepage_for_site(self, item):
        site_path = item.text(2)
        homepage_files = [f for f in os.listdir(site_path) if f.lower() in ["index.html", "index.htm", "index.php", "default.html", "default.htm"]]
        if not homepage_files:
            QMessageBox.warning(self, "Aucun fichier d'accueil", "Aucun fichier d'accueil trouvé dans ce dossier.")
            return
        current_homepage = item.text(3).split("/")[-1]
        homepage, ok = QInputDialog.getItem(self, "Changer la page d'accueil", "Choisissez la nouvelle page d'accueil :", homepage_files, 0, False)
        if ok and homepage:
            if homepage == current_homepage:
                return
            confirm = QMessageBox.question(self, "Confirmer", f"Changer la page d'accueil en '{homepage}' ?")
            if confirm == QMessageBox.Yes:
                # Met à jour l'URL
                prefix = item.text(0)
                url = f"http://localhost:8020{prefix}/{homepage}" if not prefix.endswith("/") else f"http://localhost:8020{prefix}{homepage}"
                item.setText(3, url)
                self.sites_tree.setItemWidget(item, 3, self._make_url_label(url))
                self.log(f"🏠 Page d'accueil changée pour {prefix}: {homepage}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Style moderne
    app.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #ecf0f1;
            font-family: Arial, sans-serif;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #bdc3c7;
            border-radius: 5px;
            margin-top: 1ex;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QTreeWidget, QListWidget, QTextEdit, QTableWidget {
            border: 1px solid #bdc3c7;
            border-radius: 3px;
            background-color: white;
        }
        QTabWidget::pane {
            border: 1px solid #bdc3c7;
            border-radius: 3px;
        }
        QTabBar::tab {
            background-color: #bdc3c7;
            padding: 8px 15px;
            margin-right: 2px;
            border-top-left-radius: 3px;
            border-top-right-radius: 3px;
        }
        QTabBar::tab:selected {
            background-color: #3498db;
            color: white;
        }
    """)
    
    window = SitePanel()
    window.show()
    sys.exit(app.exec_())