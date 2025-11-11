import sys
from dez.memcache import get_memcache
from dez.http.application import HTTPApplication
from .logger import logger_getter
from .routes import static, cb
from .config import config
sys.path.insert(0, ".") # for dynamically loading modules

class WebBase(HTTPApplication):
    def __init__(self, bind_address, port, logger_getter, static=static, cb=cb, whitelist=[], blacklist=[], shield=False, mempad=0):
        isprod = config.mode == "production"
        HTTPApplication.__init__(self, bind_address, port, logger_getter, "dez/cantools",
            config.ssl.certfile, config.ssl.keyfile, config.ssl.cacerts,
            isprod, config.web.rollz, isprod, whitelist, blacklist, shield, mempad, config.web.xorigin)
        self.memcache = get_memcache()
        self.handlers = {}
        for key, val in list(static.items()):
            self.add_static_rule(key, val)
        for key, val in list(cb.items()):
            self.add_cb_rule(key, self._handler(key, val))

    def _handler(self, rule, target):
        self.logger.info("setting handler: %s %s"%(rule, target))
        def h(req):
            self.logger.info("triggering handler: %s %s"%(rule, target))
            self.controller.trigger_handler(rule, target, req)
        return h

class Web(WebBase):
    def __init__(self, bind_address, port, logger_getter, shield, mempad):
        self.logger = logger_getter("Web")
        wcfg = config.web
        WebBase.__init__(self, bind_address, port, logger_getter,
            whitelist=wcfg.whitelist, blacklist=wcfg.blacklist, shield=shield, mempad=mempad)

webs = {}
def addWeb(name, daemon, cfg):
    webs[name] = daemon
    if config.webs[name]:
        for key, val in cfg.items():
            config.webs[name].update(key, val)
    else:
        config.webs.update(name, cfg)

def initWebs(extras={}):
    addWeb("web", Web, config.web)
    for web, cfg in extras.items():
        addWeb(web, cfg["daemon"], cfg["config"])