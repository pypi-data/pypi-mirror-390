README - Py Protector Prototype

Ce dépôt contient un prototype minimal pour:
1) compiler et chiffrer un projet Python (encrypt_project.py)
2) déchiffrer et exécuter le bytecode en mémoire (launcher.py)
3) packager le runtime embeddable + fichiers chiffrés (packager.py)

Pré-requis:
- Python 3.10+
- pip install pycryptodome

Usage rapide:
1) Place ton point d'entrée (ex: main.py) dans project_src/
2) python encrypt_project.py --src project_src --out build_encrypted --password "MonMotDePasseFort"
3) python packager.py --embedded-python PATH_TO_PYTHON_EMBEDDABLE --encrypted-dir build_encrypted --out MyApp
4) MyApp\python_embedded\python.exe launcher.py

Sécurité:
- La clé est dérivée du mot de passe via PBKDF2.
- Le bytecode est chargé en mémoire (pas d'écriture en clair).
