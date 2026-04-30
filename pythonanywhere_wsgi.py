import sys
import os

path = '/home/Adul69/muse-ai'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DEMO_MODE'] = 'true'
os.environ['SECRET_KEY'] = 'pa-secret-key'
os.environ['SESSION_TYPE'] = 'filesystem'

from app import app as application
