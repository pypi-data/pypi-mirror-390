import tracemalloc, psutil, rel
from fyg.util import log as syslog
from dez.logging import get_logger_getter
from .config import config

logger_getter = get_logger_getter("httpd", syslog, config.log.allow)

_LOG = None

def setlog(f):
    global _LOG
    _LOG = f

def log(*args, **kwargs):
	if _LOG:
		_LOG(*args, **kwargs)
	else:
	    print(args, kwargs)

TMSNAP = None

def log_tracemalloc():
	global TMSNAP
	snapshot = tracemalloc.take_snapshot()
	syslog("[LINEMALLOC START]", important=True)
	if TMSNAP:
		lines = snapshot.compare_to(TMSNAP, 'lineno')
	else:
		lines = snapshot.statistics("lineno")
	TMSNAP = snapshot
	for line in lines[:10]:
		syslog(line)
	syslog("[LINEMALLOC END]", important=True)
	return True

PROC = None

def log_openfiles():
	global PROC
	if not PROC:
		PROC = psutil.Process(os.getpid())
	ofz = PROC.open_files()
	if config.log.oflist:
		syslog("OPEN FILES: %s"%(ofz,), important=True)
	else:
		syslog("OPEN FILE COUNT: %s"%(len(ofz),), important=True)
	return True

def log_kernel():
	log(json.dumps(rel.report()), "kernel")
	return True

