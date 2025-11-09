import sys, rel, traceback
from urllib.parse import unquote
from fyg.util import basiclog as log
from .converters import enc, dec, rec_conv, processResponse
from .setters import local
from .loaders import cgi_load
from ..config import config

def _send(data):
    send = local("send")
    if send:
        send(data)
    else:
        print(data)

def _close():
    local("close", sys.exit)()

def _pre_close():
    pass

def set_pre_close(f):
    global _pre_close
    _pre_close = f

def _env(html):
    return "%s"

def set_env(f):
    global _env
    _env = f

def _header(hkey, hval):
    header = local("header")
    if header:
        header(hkey, hval)
    else:
        _send("%s: %s"%(hkey, hval))

def _headers(headers):
    for k, v in list(headers.items()):
        _header(k, v)
    if config.web.server == "gae":
        _send("")

def _write(data, exit=True, savename=None):
    if savename:
        from ..memcache import setmem
        setmem(savename, data, False)
    _send(data)
    if exit:
        _pre_close()
        _close()

FILETYPES = {"pdf": "application/pdf", "img": "image/png", "ico": "image/ico", "html": "text/html"}

def send_pdf(data, title=None):
    if title:
        _headers({
            "Content-Type": 'application/pdf; name="%s.pdf"'%(title,),
            "Content-Disposition": 'attachment; filename="%s.pdf"'%(title,)
        })
    else:
        _headers({"Content-Type": "application/pdf"})
    _send(data)
    _close()

def send_image(data):
    _headers({"Content-Type": "image/png"})
    _send(data)
    _close()

def send_file(data, file_type=None, detect=False, headers={}):
    if detect:
        import magic
        file_type = data and magic.from_buffer(data, True)
    if file_type:
        headers["Content-Type"] = FILETYPES.get(file_type, file_type)
    _headers(headers)
    _send(data)
    _close()

def send_text(data, dtype="html", fname=None, exit=True, headers={}):
    headers["Content-Type"] = "text/%s"%(dtype,)
    if fname:
        headers['Content-Disposition'] = 'attachment; filename="%s.%s"'%(fname, dtype)
    _headers(headers)
    _write(data, exit)

def send_xml(data):
    send_text(data, "xml")

def trysavedresponse(key=None):
    from ..memcache import getmem
    key = key or local("request_string")
    response = getmem(key, False)
    response and _write(response, exit=True)

def redirect(addr, msg="", noscript=False, exit=True, metas=None):
    a = "<script>"
    if msg:
        a += 'alert("%s"); '%(msg,)
    a += "document.location = '%s';</script>"%(addr,)
    if noscript:
        a += '<noscript>This site requires Javascript to function properly. To enable Javascript in your browser, please follow <a href="http://www.google.com/support/bin/answer.py?answer=23852">these instructions</a>. Thank you, and have a nice day.</noscript>'
    if metas:
        a = "<html><head>%s%s</head><body></body></html>"%(metas, a)
    _header("Content-Type", "text/html")
    _write(_env(True)%(a,), exit)

def resp_wrap(resp, failure):
    def f():
        try:
            resp()
        except rel.errors.AbortBranch as e:
            _pre_close()
            raise rel.errors.AbortBranch() # handled in rel
        except SystemExit:
            pass
        except Exception as e:
            failure(e)
    return f

def succeed_sync(func, cb):
    d = {}
    def handle(*a, **k):
        d["a"] = a
        d["k"] = k
    func(handle)
    while True:
        time.sleep(0.01)
        if d["a"] or d["k"]:
            succeed(cb(*d["a"], **d["k"]))

def succeed(data="", html=False, noenc=False, savename=None, cache=False):
    if cache or config.memcache:
        savename = local("request_string")
    _header("Content-Type", "text/%s"%(html and "html" or "plain"))
    draw = processResponse(data, "1")
    dstring = (config.encode and not noenc) and enc(draw) or draw
    _write(_env(html)%(dstring,), savename=savename)

def fail(data="failed", html=False, err=None, noenc=False, exit=True):
    if err:
        # log it
        logdata = "%s --- %s --> %s"%(data, repr(err), traceback.format_exc())
        log("error:", logdata)
        if config.web.debug:
            # write it
            data = logdata
        resp = local("response")
        reqstring = local("request_string")
        path = resp and resp.request.url or "can't find path!"
        ip = local("ip") or (resp and resp.ip or "can't find ip!")
        edump = "%s\n\n%s\n\n%s\n\n%s"%(path, ip, reqstring, logdata)
        shield = config.web.shield
        if reqstring and shield(reqstring, ip):
            data = "nabra"
            reason = shield.ip(ip)["message"]
            logline = "%s - IP (%s) banned!"%(reason, ip)
            edump = "%s\n\n%s"%(logline, edump)
            log(logline)
        elif config.web.eflags:
            samples = {
                "traceback": logdata
            }
            if reqstring:
                samples["request"] = reqstring
            for sample in samples:
                for ef in config.web.eflags:
                    if ef in samples[sample]:
                        reason = '"%s" in %s'%(ef, sample)
                        logline = "%s - IP (%s) banned!"%(reason, ip)
                        edump = "%s\n\n%s"%(logline, edump)
                        shield.suss(ip, reason)
                        log(logline)
        if config.web.report:
            from .mail import email_admins
            email_admins("error encountered", edump)
    _header("Content-Type", "text/%s"%(html and "html" or "plain"))
    draw = processResponse(data, "0")
    dstring = (config.encode and not noenc) and enc(draw) or draw
    _write(_env(html)%(dstring,), exit)

def do_respond(responseFunc, failMsg="failed", failHtml=False, failNoEnc=False, noLoad=False, threaded=False, response=None, autowin=True):
    def resp():
        response and response.set_cbs()
        noLoad or cgi_load()
        responseFunc()
        autowin and succeed()

    def failure(e):
        fail(data=failMsg, html=failHtml, err=e, noenc=failNoEnc)

    wrapped_response = resp_wrap(resp, failure)
    if threaded:
        rel.thread(wrapped_response)
    else:
        wrapped_response()