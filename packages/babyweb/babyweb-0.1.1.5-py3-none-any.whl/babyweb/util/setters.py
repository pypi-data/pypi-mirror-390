import threading

localvars = threading.local()
def local(key, fallback=None):
    return getattr(localvars, key, fallback)

def set_read(f):
    localvars.read = f

def set_send(f):
    localvars.send = f

def set_redir(f):
    localvars.redir = f

def set_header(f):
    localvars.header = f

def set_close(f):
    localvars.close = f
