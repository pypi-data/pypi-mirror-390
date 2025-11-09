import json, cgi, ast, sys
from base64 import b64decode
from urllib.parse import unquote
from .setters import local, localvars
from .converters import dec, rec_conv
from ..config import config

def qs_get(x, y):
    val = localvars.request.getvalue(x, y)
    if val:
        val = unquote(val)
    return val

def cgi_read():
    return local("read", sys.stdin.read)()

def cgi_dump():
    return local("request_string")

def cgi_load():
    localvars.request_string = cgi_read()
    data = config.encode and dec(localvars.request_string) or localvars.request_string
    try:
        try:
            jdata = json.loads(data)
        except:
            jdata = ast.literal_eval(data)
        try:
            localvars.request = rec_conv(jdata, True)
        except:
            localvars.request = jdata
    except:
        localvars.request = cgi.FieldStorage()
        setattr(localvars.request, "get", qs_get)
    if not localvars.request:
        localvars.request = {}

def cgi_get(key, choices=None, required=True, default=None, shield=False, decode=False, base64=False):
    from .responders import fail
    request = local("request")
    val = request.get(key, default)
    if val is None:
        required and fail('no value submitted for required field: "%s" [%s]'%(key, request))
    elif shield:
        ip = local("ip")
        shield = config.web.shield
        if shield(val, ip, fspath=True, count=False):
            log('cgi_get() shield bounced "%s" for "%s"'%(ip, shield.ip(ip)["message"]))
            fail()
    if choices and val not in choices:
        fail('invalid value for "%s": "%s"'%(key, val))
    if base64 and val:
        val = b64decode(unquote(val))
    if decode and val:
        val = unquote(val)
    return val