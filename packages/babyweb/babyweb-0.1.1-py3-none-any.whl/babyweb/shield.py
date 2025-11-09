import os
from dez.http.server.shield import Shield
from fyg.util import read, write
from .logger import logger_getter
from .config import config

class PaperShield(object):
	def __init__(self):
		self.logger = logger_getter("PaperShield")
		self.default = { "reason": "I'm just a paper shield!" }
		self.ips = {}

	def __call__(self, path, ip, fspath=False, count=True):
		self.logger.access('NOOP > paperShield("%s", "%s", fspath=%s, count=%s)'%(path, ip, fspath, count))

	def suss(self, ip, reason):
		self.logger.access("suss(%s) -> %s"%(ip, reason))
		self.ips[ip] = { "reason": reason }

	def ip(self, ip):
		return self.ips.get(ip, self.default)

def setShield(blup=None):
	shield = None
	shfg = config.web.shield
	if shfg: # web/admin share shield and blacklist
		setBlacklist()
		shield = Shield(config.web.blacklist, logger_getter, blup or writeBlacklist,
			getattr(shfg, "limit", 400),
			getattr(shfg, "interval", 2))
	config.web.update("shield", shield or PaperShield())
	return shield

def setBlacklist():
	bl = {}
	for preban in config.web.blacklist:
		bl[preban] = "config ban"
	if os.path.isfile("black.list"):
		try:
			bsaved = read("black.list", isjson=True)
		except: # old style
			bsaved = {}
			for line in read("black.list", lines=True):
				bsaved[line.strip()] = "legacy ban"
		bsaved and bl.update(bsaved)
	config.web.update("blacklist", bl)

def writeBlacklist():
	wcfg = config.web
	bl = wcfg.blacklist.obj()
	write(bl, "black.list", isjson=True)
	wcfg.blacklister and wcfg.blacklister.update(bl)
	return len(bl.keys())