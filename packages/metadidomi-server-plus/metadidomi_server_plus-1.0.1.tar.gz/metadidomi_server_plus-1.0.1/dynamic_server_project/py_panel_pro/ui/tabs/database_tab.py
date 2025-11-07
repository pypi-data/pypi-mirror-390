import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QListWidget, QMessageBox, QInputDialog, QTableWidget, QTableWidgetItem)
from core.db_manager import MySQLManager

class DatabaseTab(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.manager = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        conn_row = QHBoxLayout()
        conn_row.addWidget(QLabel('Host'))
        self.host = QLineEdit('127.0.0.1')
        conn_row.addWidget(self.host)
        conn_row.addWidget(QLabel('User'))
        self.user = QLineEdit('root')
        conn_row.addWidget(self.user)
        conn_row.addWidget(QLabel('Pass'))
        self.pw = QLineEdit('')
        self.pw.setEchoMode(QLineEdit.Password)
        conn_row.addWidget(self.pw)
        btn_conn = QPushButton('🔌 Connecter')
        btn_conn.clicked.connect(self.connect_db)
        conn_row.addWidget(btn_conn)
        layout.addLayout(conn_row)

        self.db_list = QListWidget()
        self.db_list.itemClicked.connect(self.on_db_select)
        layout.addWidget(self.db_list)

        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        ops = QHBoxLayout()
        btn_refresh = QPushButton('🔄 Refresh DBs')
        btn_refresh.clicked.connect(self.refresh_dbs)
        ops.addWidget(btn_refresh)
        btn_show = QPushButton('Afficher tables')
        btn_show.clicked.connect(self.show_tables)
        ops.addWidget(btn_show)
        btn_rows = QPushButton('Voir lignes')
        btn_rows.clicked.connect(self.show_rows)
        ops.addWidget(btn_rows)
        layout.addLayout(ops)
        self.setLayout(layout)

    def connect_db(self):
        host = self.host.text().strip()
        user = self.user.text().strip()
        pw = self.pw.text()
        self.manager = MySQLManager(host=host, user=user, password=pw)
        ok, err = self.manager.connect()
        if not ok:
            QMessageBox.critical(self, 'Erreur', f'Impossible de se connecter: {err}')
            return
        QMessageBox.information(self, 'Connecté', 'Connexion MySQL OK')
        self.refresh_dbs()

    def refresh_dbs(self):
        if not self.manager or not self.manager.conn:
            return
        try:
            dbs = self.manager.list_databases()
            self.db_list.clear()
            for d in dbs:
                self.db_list.addItem(d)
        except Exception as e:
            QMessageBox.critical(self, 'Erreur', str(e))

    def on_db_select(self, item):
        self.current_db = item.text()

    def show_tables(self):
        if not self.manager or not self.manager.conn:
            QMessageBox.warning(self, 'Info', 'Connecte-toi d'abord.')
            return
        db = getattr(self, 'current_db', None)
        if not db:
            QMessageBox.warning(self, 'Info', 'Sélectionne une DB.')
            return
        try:
            tables = self.manager.list_tables(db)
            QMessageBox.information(self, 'Tables', '\n'.join(tables))
        except Exception as e:
            QMessageBox.critical(self, 'Erreur', str(e))

    def show_rows(self):
        if not self.manager or not self.manager.conn:
            QMessageBox.warning(self, 'Info', 'Connecte-toi d'abord.')
            return
        db = getattr(self, 'current_db', None)
        if not db:
            QMessageBox.warning(self, 'Info', 'Sélectionne une DB.')
            return
        tbl, ok = QInputDialog.getText(self, 'Table', 'Nom de la table:')
        if not ok or not tbl:
            return
        rows = self.manager.fetch_rows(db, tbl, limit=200)
        if not rows:
            QMessageBox.information(self, 'Rows', 'Aucune ligne trouvée ou table vide.')
            return
        # display in table widget (first row keys)
        cols = list(rows[0].keys())
        self.table_widget.setColumnCount(len(cols))
        self.table_widget.setRowCount(len(rows))
        self.table_widget.setHorizontalHeaderLabels(cols)
        for r, row in enumerate(rows):
            for c, col in enumerate(cols):
                self.table_widget.setItem(r, c, QTableWidgetItem(str(row.get(col, ''))))
