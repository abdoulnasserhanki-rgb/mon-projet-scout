import os
import sys
import subprocess

# Chemin du projet
project_path = '/home/anyhtech/public_html/scout'
sys.path.insert(0, project_path)

# Essayer d'importer Django
try:
    from django.core.wsgi import get_wsgi_application
except ImportError:
    # Si Django n'est pas installé, essayer de l'installer
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Django==4.2.7'])
        from django.core.wsgi import get_wsgi_application
    except Exception as e:
        raise ImportError(f"Impossible d'installer Django: {e}")

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scout.settings')
application = get_wsgi_application()