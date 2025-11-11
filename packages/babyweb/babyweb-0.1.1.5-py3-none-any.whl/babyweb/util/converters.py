import json
from urllib.parse import quote, unquote
from base64 import b64encode, b64decode
from six import string_types
from ..config import config

_c = config.scrambler
_cl = len(_c)
_chl = int(_cl / 2)

def flip(c):
    i = _c.find(c)
    if i == -1:
        return c
    return _c[(i + _chl) % _cl]

def scramble(s):
    return "".join([flip(c) for c in s])

def enc(data):
    return scramble(b64encode(hasattr(data, "encode") and data.encode() or data).decode())

def dec(data):
    return data.startswith("{") and data or b64decode(scramble(data)).decode()

def setenc(f):
    global enc
    enc = f

def setdec(f):
    global dec
    dec = f

def rdec(data):
    return unquote(b64decode(data.encode()).decode())

def renc(data):
    return b64encode(quote(data).encode()).decode()

def rec_conv(data, de=False):
    if isinstance(data, bytes):
        try:
            data = data.decode()
        except:
            pass
    if isinstance(data, string_types):
        return (de and rdec or renc)(data)
    elif isinstance(data, dict):
        for k, v in list(data.items()):
            data[k] = rec_conv(v, de)
    elif isinstance(data, list):
        return [rec_conv(d, de) for d in data]
    return data

def processResponse(data, code):
    if code == "1":
        try:
            data = json.dumps(data)
        except:
            data = json.dumps(rec_conv(data))
            code = "3"
    elif code == "0":
        try:
            json.dumps(data)
        except:
            data = rec_conv(data)
            code = "2"
    return "%s%s"%(code, data)

