# AUTOGENERATED! DO NOT EDIT! File to edit: 00_core.ipynb (unless otherwise specified).

__all__ = ['clean_tweet_body', 'tweet_text', 'check_sig', 'reconfig', 'run_server', 'fastwebhook_install_service']

# Cell
import json,tweepy,hmac,hashlib,traceback,shutil,time,fcntl,re

from fastcore.imports import *
from fastcore.foundation import *
from fastcore.utils import *
from fastcore.script import *
from fastcore.meta import *
from fastcore.test import *
from configparser import ConfigParser
from ipaddress import ip_address,ip_network
from socketserver import ThreadingTCPServer
from fastcgi.http import MinimalHTTPHandler
from fastcgi import ReuseThreadingServer
from ghapi.all import GhApi

from textwrap import dedent

# Cell
def clean_tweet_body(body):
    "Cleans links and sets proper @'s in the tweet body"
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', body)
    for issue, link in links:
        str_replace = ""
        if "@" in issue:
            str_replace = issue[1:]
            username = GhApi().users.get_by_username(str_replace).twitter_username
            if username: str_replace = f"@{username}"
            original_link = f"[{issue}]({link})"
        else: original_link = f" ([{issue}]({link}))"
        body = body.replace(original_link, str_replace)
    body = body.replace("### ", "")
    return body

# Cell
def tweet_text(payload):
    "Send a tweet announcing release based on `payload`"
    rel_json = payload['release']
    url = rel_json['url']
    owner,repo = re.findall(r'https://api.github.com/repos/([^/]+)/([^/]+)/', url)[0]
    tweet_tmpl = "New #{repo} release: v{tag_name}. {html_url}\n\n{body}"
    res = tweet_tmpl.format(repo=repo, tag_name=rel_json['tag_name'],
                            html_url=rel_json['html_url'], body=clean_tweet_body(rel_json['body']))
    if len(res)<=280: return res
    return res[:279] + "…"

# Cell
def check_sig(content, headers, secret):
    digest = hmac.new(secret, content, hashlib.sha1).hexdigest()
    assert f'sha1={digest}' == headers.get('X-Hub-Signature')

# Cell
class _RequestHandler(MinimalHTTPHandler):
    def _post(self):
        assert self.command == 'POST'
        if self.server.check_ip:
            src_ip = re.split(', *', self.headers.get('X-Forwarded-For', ''))[0] or self.client_address[0]
            src_ip = ip_address(src_ip)
            assert any((src_ip in wl) for wl in self.server.whitelist)
        self.send_response(200)
        self.end_headers()
        length = self.headers.get('content-length')
        if not length: return
        content = self.rfile.read(int(length))
        if self.server.debug:
            print(self.headers, content)
            return
        payload = json.loads(content.decode())
        if payload.get('action',None)=='released':
            check_sig(content, self.headers, self.server.gh_secret)
            tweet = tweet_text(payload)
            stat = self.server.api.update_status(tweet)
            print(stat.id)
        self.wfile.write(b'ok')

    def handle(self):
        try: self._post()
        except Exception as e: sys.stderr.write(traceback.format_exc())

    def log_message(self, fmt, *args): sys.stderr.write(fmt%args)

# Cell
def reconfig(s):
    if hasattr(s, 'reconfigure'): return s.reconfigure(line_buffering=True)
    try:
        fl = fcntl.fcntl(s.fileno(), fcntl.F_GETFL)
        fl |= os.O_SYNC
        fcntl.fcntl(s.fileno(), fcntl.F_SETFL, fl)
    except io.UnsupportedOperation: pass

# Cell
@call_parse
def run_server(
    hostname:str='localhost',  # Host name or IP
    port:int=8000,  # Port to listen on
    debug:bool_arg=False,  # If True, do not trigger actions, just print
    inifile:str='twitter.ini',  # Path to settings ini file
    check_ip:bool_arg=True,  # Check source IP against GitHub list
    single_request:bool_arg=False  # Handle one request
):
    "Run a GitHub webhook server that tweets about new releases"
    assert os.path.exists(inifile), f"{inifile} not found"
    cfg = ConfigParser(interpolation=None)
    cfg.read([inifile])
    cfg = cfg['DEFAULT']
    auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
    auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
    os.environ['PYTHONUNBUFFERED'] = '1'
    print(f"Listening on {(hostname,port)}")

    with ReuseThreadingServer((hostname, port), _RequestHandler) as httpd:
        httpd.gh_secret = bytes(cfg['gh_secret'], 'utf-8')
        httpd.api = tweepy.API(auth)
        httpd.whitelist = L(urljson('https://api.github.com/meta')['hooks']).map(ip_network)
        httpd.check_ip,httpd.debug = check_ip,debug
        if single_request: httpd.handle_request()
        else:
            try: httpd.serve_forever()
            except KeyboardInterrupt: print("Closing")

# Cell
@call_parse
def fastwebhook_install_service(
    hostname:str='0.0.0.0',  # Host name or IP
    port:int=8000,  # Port to listen on
    inifile:str='twitter.ini',  # Path to settings ini file
    check_ip:bool_arg=True,  # Check source IP against GitHub list
    service_path:str="/etc/systemd/system/"  # Directory to write service file to
):
    "Install fastwebhook as a service"
    script_loc = shutil.which('fastwebhook')
    inifile = Path(inifile).absolute()
    _unitfile = dedent(f"""
    [Unit]
    Description=fastwebhook
    Wants=network-online.target
    After=network-online.target

    [Service]
    ExecStart={script_loc} --inifile {inifile} --check_ip {check_ip} --hostname {hostname} --port {port}
    Restart=always

    [Install]
    WantedBy=multi-user.target""")
    Path("fastwebhook.service").write_text(_unitfile)
    run(f"sudo cp fastwebhook.service {service_path}")