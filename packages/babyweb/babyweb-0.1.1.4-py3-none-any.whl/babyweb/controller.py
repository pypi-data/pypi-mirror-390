import os, sys, platform
from dez.network import SocketController, daemon_wrapper
from .shield import setShield, writeBlacklist
from .logger import logger_getter
from .response import Response
from .daemons import webs
from .cron import Cron
from .version import __version__
from .util import do_respond, localvars
from .config import config

CTR = None

class Controller(SocketController):
	def __init__(self, *args, **kwargs):
		self.logger = logger_getter("Controller")
		SocketController.__init__(self, *args, **kwargs)
		self.handlers = {}
		self.modules = {}
		self.webs = {}
		self.blcount = 0
		self.blchunk = getattr(config.web.shield, "chunk", 5)
		self.logger.info("babyweb: %s"%(__version__,))
		self.logger.info("Python: %s"%(sys.version.split(' ')[0],))
		self.logger.info("System: " + " > ".join([part for part in platform.uname() if part]))

	def _respond(self, resp, *args, **kwargs):
		if resp == "nothread": # "on start nothread" cron
			kwargs["noLoad"] = True
		elif resp: # regular request
			kwargs["response"] = resp
			localvars.response = resp
		else: # regular cron
			kwargs["noLoad"] = True
			kwargs["threaded"] = True
		do_respond(*args, **kwargs)

	def register_handler(self, args, kwargs):
		self.logger.info("register handler: %s"%(self.curpath,))
		self.handlers[self.curpath] = lambda resp : self._respond(resp, *args, **kwargs)

	def trigger_handler(self, rule, target, req=None, option=None):
		self.curpath = rule
		if rule not in self.handlers:
			if target in self.modules:
				self.logger.info("linking module: %s"%(target,))
				self.handlers[rule] = self.modules[target]
			else:
				self.logger.info("importing module: %s"%(target,))
				__import__(target)
				self.modules[target] = self.handlers[rule]
		self.handlers[rule](req and Response(req) or option)

	def blup(self):
		blen = writeBlacklist()
		self.logger.warn("saved %s IPs in black.list"%(blen,))
		if self.blcount != blen:
			self.blcount = blen
			if config.web.report and not blen % self.blchunk:
				from .mail import email_admins
				email_admins("sketch IPs blacklisted", "sketch count: %s"%(blen,))

	def web(self, name, cfg, daemon, shield):
		self.webs[name] = self.register_address(cfg.host,
			cfg.port, dclass=daemon_wrapper(daemon, logger_getter, shield, config.mempad))
		self.webs[name].controller = self

def getController():
	global CTR
	if not CTR:
		# controller
		CTR = Controller()
		shield = setShield(CTR.blup)
		mempad = config.mempad

		for web in webs:
			CTR.web(web, config.webs[web], webs[web], shield)

		# cron
		Cron(CTR, logger_getter)

	return CTR

def dweb(wname="web"):
	return getController().webs.get(wname)

def respond(*args, **kwargs):
	getController().register_handler(args, kwargs)

