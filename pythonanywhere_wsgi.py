import sys
import os

# Debug: print Python version and path
print("=" * 60, file=sys.stderr)
print("PYTHON VERSION:", sys.version, file=sys.stderr)
print("PYTHON PATH:", sys.path, file=sys.stderr)

# Add project path
path = '/home/Adul69/muse-ai'
if path not in sys.path:
    sys.path.insert(0, path)
print("ADDED PATH:", path, file=sys.stderr)

# List files in project dir to verify
print("FILES IN PROJECT DIR:", os.listdir(path) if os.path.exists(path) else "PATH NOT FOUND", file=sys.stderr)

# Set env vars BEFORE importing app
os.environ['DEMO_MODE'] = 'true'
os.environ['SECRET_KEY'] = 'pa-secret-key'
os.environ['SESSION_TYPE'] = 'filesystem'
os.environ['PYTHONUNBUFFERED'] = 'true'

# Import with error catching
try:
    from app import app as application
    print("APP IMPORTED SUCCESSFULLY", file=sys.stderr)
except Exception as e:
    print("IMPORT ERROR:", type(e).__name__, str(e), file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    raise
