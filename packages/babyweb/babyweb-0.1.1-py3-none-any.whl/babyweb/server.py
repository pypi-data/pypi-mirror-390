import os, time, requests, rel, ssl, sys, json, resource, tracemalloc, psutil
from fyg.util import log, set_log, set_error
from .logger import setlog, logger_getter, log_tracemalloc, log_openfiles, log_kernel
from .controller import getController
from .util import fail
from .config import config

def fdup():
	log("checking the number of file descriptors allowed on your system", important=True)
	soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
	half = int(hard / 2)
	log("soft: %s. hard: %s. half: %s"%(soft, hard, half))
	if soft < half:
		log("increasing soft limit to half of hard limit")
		resource.setrlimit(resource.RLIMIT_NOFILE, (half, hard))
		log("new limits! soft: %s. hard: %s"%resource.getrlimit(resource.RLIMIT_NOFILE))

def quit():
	if config.errlog:
		log("closing error log", important=True)
		sys.stderr.close()
	log("quitting - goodbye!", important=True)

def run_dez_webserver():
	if not config.ssl.verify and hasattr(ssl, "_https_verify_certificates"):
		ssl._https_verify_certificates(False)
	c = getController()
	setlog(c.webs["web"].logger.simple)
	if config.web.log:
		set_log(os.path.join("logs", config.web.log))
	clog = config.log
	if clog.openfiles:
		rel.timeout(clog.openfiles, log_openfiles)
	if clog.tracemalloc:
		tracemalloc.start()
		rel.timeout(clog.tracemalloc, log_tracemalloc)
	if "kernel" in clog.allow:
		rel.timeout(1, log_kernel)
	set_error(fail)
	if config.fdup:
		fdup()
	if config.web.errlog:
		sys.stderr = open(os.path.join("logs", config.web.errlog), "a")
	c.start(quit)

if __name__ == "__main__":
	run_dez_webserver()