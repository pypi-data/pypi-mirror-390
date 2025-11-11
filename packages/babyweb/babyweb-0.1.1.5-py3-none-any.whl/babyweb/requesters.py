import time, requests, json
from dez.http import fetch as dfetch, post as dpost
from fyg.util import log
from .util import rec_conv, dec

def _ctjson(result):
	if hasattr(result, "decode"):
		result = result.decode()
	code = result[0]
	if code not in "0123":
		log("response encoded:")
		log(result)
		log("attempting decode")
		result = dec(result)
	if code in "02":
		log("request failed!! : %s"%(result,), important=True)
	elif code == "3":
		return rec_conv(json.loads(result[1:]), True)
	else:
		return json.loads(result[1:])

def parse_url_parts(host, path, port, protocol):
	if "://" in host:
		protocol, host = host.split("://", 1)
		if "/" in host:
			host, path = host.split("/", 1)
			path = "/" + path
		else:
			path = "/"
	if ":" in host:
		host, port = host.split(":")
		port = int(port)
	elif not port:
		port = protocol == "https" and 443 or 80
	return host, path, port, protocol

def fetch(host, path="/", port=None, asjson=False, cb=None, timeout=1, asyn=False, protocol="http", ctjson=False, qsp=None, fakeua=False, retries=5):
	host, path, port, protocol = parse_url_parts(host, path, port, protocol)
	if qsp:
		path += "?"
		for k, v in list(qsp.items()):
			path += "%s=%s&"%(k, v)
		path = path[:-1]
	gkwargs = {}
	headers = {}
	if fakeua:
		if type(fakeua) is str:
			headers['User-Agent'] = fakeua
		else:
			headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36'
		gkwargs["headers"] = headers
	if asyn or cb: # asyn w/o cb works, will just log
		secure = protocol == "https"
		if ctjson:
			orig_cb = cb or log
			cb = lambda v : orig_cb(_ctjson(v))
		return dfetch(host, path, port, secure, headers, cb, timeout, asjson)
	if timeout:
		gkwargs["timeout"] = timeout
	furl = "%s://%s:%s%s"%(protocol, host, port, path)
	log("fetch %s"%(furl,))
	return syncreq(furl, "get", asjson, ctjson, retries, gkwargs)

def post(host, path="/", port=80, data=None, protocol="http", asjson=False, ctjson=False, text=None, cb=None):
	if ctjson:
		data = rec_conv(data)
	if cb:
		if ctjson:
			orig_cb = cb
			cb = lambda v : orig_cb(_ctjson(v))
		host, path, port, protocol = parse_url_parts(host, path, port, protocol)
		return dpost(host, path, port, protocol == "https", data=data, text=text, cb=cb)
	url = "://" in host and host or "%s://%s:%s%s"%(protocol, host, port, path)
	log("post %s"%(url,))
	kwargs = {}
	if data:
		kwargs["json"] = data
	elif text:
		kwargs["data"] = text
	return syncreq(url, "post", asjson, ctjson, rekwargs=kwargs)

def _dosyncreq(requester, url, asjson, ctjson, rekwargs):
	result = requester(url, **rekwargs).content
	if ctjson:
		return _ctjson(result)
	return asjson and json.loads(result) or result

def syncreq(url, method="get", asjson=False, ctjson=False, retries=5, rekwargs={}):
	attempt = 1
	requester = getattr(requests, method)
	while attempt < retries:
		try:
			return _dosyncreq(requester, url, asjson, ctjson, rekwargs)
		except requests.exceptions.ConnectionError:
			log("syncreq(%s %s) attempt #%s failed"%(method, url, attempt))
			time.sleep(1)
		attempt += 1
	return _dosyncreq(requester, url, asjson, ctjson, rekwargs) # final try-less try
