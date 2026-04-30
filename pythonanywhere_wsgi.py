import sys
path = '/home/yourusername/muse-ai'
if path not in sys.path:
    sys.path.insert(0, path)

import os
os.environ['DEMO_MODE'] = 'true'
os.environ['SECRET_KEY'] = 'pythonanywhere-secret-key'
os.environ['SESSION_TYPE'] = 'filesystem'

from app import app as application
