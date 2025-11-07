import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from ui.main_window import PyPanelMainWindow
import os

if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    app = QApplication(sys.argv)
    # apply dark style if available
    try:
        import qdarkstyle
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    except Exception:
        pass
    window = PyPanelMainWindow()
    window.show()
    QMessageBox.warning(window, 'Info', 'Le projet n\'a pas de port configuré. Démarre-le d\'abord.')
    sys.exit(app.exec_())
