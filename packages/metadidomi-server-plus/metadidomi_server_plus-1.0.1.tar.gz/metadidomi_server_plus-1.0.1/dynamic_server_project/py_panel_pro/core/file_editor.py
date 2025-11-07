from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
PROJECTS_DIR = BASE / 'projects'

def list_files(project_name):
    p = PROJECTS_DIR / project_name
    if not p.exists():
        return []
    return [str(x.relative_to(p)) for x in p.rglob('*') if x.is_file()]

def read_file(project_name, relpath):
    p = PROJECTS_DIR / project_name / relpath
    if not p.exists():
        raise FileNotFoundError('Fichier introuvable')
    return p.read_text(encoding='utf-8')

def write_file(project_name, relpath, content):
    p = PROJECTS_DIR / project_name / relpath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')
    return True
