import tracemalloc, psutil, rel
from fyg.util import log as syslog
from dez.logging import get_logger_getter
from .config import config

logger_getter = get_logger_getter("httpd", syslog, config.log.allow)

def log(*args, **kwargs):
    print(args, kwargs)

# setters (see above)
def setlog(f):
    global log
    log = f

TMSNAP = None

def log_tracemalloc():
	global TMSNAP
	snapshot = tracemalloc.take_snapshot()
	log("[LINEMALLOC START]", important=True)
	if TMSNAP:
		lines = snapshot.compare_to(TMSNAP, 'lineno')
	else:
		lines = snapshot.statistics("lineno")
	TMSNAP = snapshot
	for line in lines[:10]:
		log(line)
	log("[LINEMALLOC END]", important=True)
	return True

PROC = None

def log_openfiles():
	global PROC
	if not PROC:
		PROC = psutil.Process(os.getpid())
	ofz = PROC.open_files()
	if config.log.oflist:
		log("OPEN FILES: %s"%(ofz,), important=True)
	else:
		log("OPEN FILE COUNT: %s"%(len(ofz),), important=True)
	return True

def log_kernel():
	log(json.dumps(rel.report()), "kernel")
	return True

