from .controller import dweb

def getmem(key, tojson=True):
	return dweb().memcache.get(key, tojson)

def setmem(key, val, fromjson=True):
	dweb().memcache.set(key, val, fromjson)

def delmem(key):
	dweb().memcache.rm(key)

def clearmem():
	dweb().memcache.clear()

def getcache():
	c = {}
	orig = dweb().memcache.cache
	for k, v in list(orig.items()):
		if v.__class__ == set:
			v = list(v)
		elif v.__class__ == dict and "ttl" in v: # countdown
			v = str(v)
		c[k] = v
	return c

