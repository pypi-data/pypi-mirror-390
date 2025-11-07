from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def get_version():
    version_file = os.path.join("app", "version.txt")
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            return f.read().strip()
    return "1.0.1"  # Version par défaut

setup(
    name="metadidomi-server-plus",
    version=get_version(),
    author="MetadidomiServerPlus Team",
    description="Un serveur avancé pour Metadidomi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/METADIDOMIOFFICIEL/Metadidomi-ServerPlus-Core",
    packages=find_packages(include=['app*', 'dynamic_server_project*', 'alembic*', 'apps*']),
    package_data={
        '': ['*.html', '*.css', '*.js', 
             '*.json', '*.pem', '*.txt',
               '*.md', '*.yml', '*.sqlite',
                 '*.db', '*.log', '*.cfg', 
                 '*.key', '*.ini', '*.pkl', 
                 '*.pem', '*.ico', '*.ps1'],
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'metadidomi-server=app.main:run_server',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        'fastapi>=0.68.0',
        'uvicorn>=0.15.0',
        'sqlalchemy>=1.4.0',
        'pydantic>=1.8.0',
        'python-multipart>=0.0.5',
        'Jinja2>=3.0.0',
        'python-dotenv>=0.19.0',
        'PyQt5>=5.15.0',
        'flask>=2.0.0',
        'flask-cors>=3.0.0',
        'flask-socketio>=5.1.0',
        'bcrypt>=3.2.0',
        'requests>=2.26.0',
        'psutil>=5.8.0',
        'Pillow>=8.0.0',
        'PyJWT>=2.1.0',
        'beautifulsoup4>=4.9.0',
        'pytesseract>=0.3.8',
        'PyYAML>=5.4.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.0.0',
            'black>=21.0.0',
            'isort>=5.0.0',
            'flake8>=3.9.0',
        ],
    },
)