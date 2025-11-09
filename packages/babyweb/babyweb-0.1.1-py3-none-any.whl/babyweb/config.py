from fyg import Config, PCache

config = Config({
	"cache": PCache(".tw"),
	"encode": False,
	"memcache": False,
	"mempad": 0, # 0 = unset (uses dez's default)
	"webs": {},
	"log": {
		"oflist": False,
		"openfiles": False,
		"tracemalloc": False,
		"allow": ["info", "log", "warn", "error"] # access,info,log,warn,error,detail,db,query,kernel
	},
	"mail": {
		"mailer": None,
		"name": None,
		"html": True,
		"gmailer": False,
		"verbose": False,
		"scantick": 2
	},
	"web": {
		"domain": "your.web.domain",
		"host": "0.0.0.0",
		"port": 8080,
		"protocol": "http",
		"xorigin": False,
		"report": False,
		"shield": False,
		"debug": False,
		"csp": None,
		"log": None,
		"errlog": None,
		"rollz": {},
		"eflags": [],
		"blacklist": [],
		"whitelist": []
	},
	"admin": {
		"contacts": [],
		"reportees": []
	},
	"ssl": {
		"verify": True,
		"certfile": None,
		"keyfile": None,
		"cacerts": None
	},
	"cron": {
		"catchup": False
	},
	"scrambler": "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/=_"
})