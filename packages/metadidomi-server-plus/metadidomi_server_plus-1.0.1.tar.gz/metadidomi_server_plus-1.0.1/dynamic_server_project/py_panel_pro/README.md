# PyPanel Pro (Python edition)
Version: PyPanel Pro - Python build (ready to run with `python main.py`)

Fonctionnalités incluses :
- Ports par projet + serveurs séparés (uvicorn subprocess pour chaque projet)
- Éditeur de fichiers intégré (éditeur simple avec sauvegarde et aperçu)
- Support MySQL (interface simple via mysql-connector-python)
- Mode autostart Windows (registry helper)
- Thème sombre (QDarkStyle) + icônes via qtawesome
- Multi-plateforme (principalement testé sur Windows + Linux)

Installation :
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Notes :
- Ce package **n'installe pas** MySQL server lui-même. Il fournit une interface pour se connecter
  à un serveur MySQL local ou distant existant via mysql-connector-python.
- Lancement des serveurs projets : chaque projet est servi par une instance uvicorn qui sert
  les fichiers statiques du dossier du projet. Ports configurables par projet.
