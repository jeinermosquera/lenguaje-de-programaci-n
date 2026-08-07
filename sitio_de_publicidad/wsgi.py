# wsgi.py — entry point WSGI para PythonAnywhere
# Configuración en el panel: WSGI config file = /home/USUARIO/.../wsgi.py
import sys
from pathlib import Path

# La raíz del proyecto (donde está app.py)
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# PythonAnywhere importa la variable "application"
from app import app as application
