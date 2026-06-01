from __future__ import annotations
import json, os
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
TOKEN='grid-quality-token'
WEB_ROOT=os.path.join(os.path.dirname(os.path.dirname(__file__)),'web')
class H(BaseHTTPRequestHandler):
  def _j(self,s,p):
    b=json.dumps(p,ensure_ascii=False).encode();self.send_response(s);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
  def _a(self): return self.headers.get('Authorization','')==f'Bearer {TOKEN}'
  def do_GET(self):
    p=urlparse(self.path).path
    if p=='/':
      with open(os.path.join(WEB_ROOT,'index.html'),'rb') as f: d=f.read();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(d)));self.end_headers();self.wfile.write(d);return
    if p.startswith('/src/'):
      fp=os.path.join(WEB_ROOT,p.lstrip('/'))
      if not os.path.exists(fp): self.send_error(404);return
      with open(fp,'rb') as f:d=f.read();self.send_response(200);self.send_header('Content-Type','text/javascript; charset=utf-8' if fp.endswith('.js') else 'text/css; charset=utf-8');self.send_header('Content-Length',str(len(d)));self.end_headers();self.wfile.write(d);return
    if p=='/api/dashboard':
      if not self._a(): return self._j(401,{'ok':False})
      return self._j(200,{'ok':True,'data':{'online_nodes':18,'high_alarms':2,'pending_controls':4,'today_reports':6}})
    if p=='/api/alarms':
      if not self._a(): return self._j(401,{'ok':False})
      return self._j(200,{'ok':True,'data':[{'code':'THD-001','level':'HIGH','title':'并网点A谐波超限'},{'code':'VUF-102','level':'MEDIUM','title':'并网点C三相不平衡'}]})
    self.send_error(404)
  def do_POST(self):
    p=urlparse(self.path).path
    n=int(self.headers.get('Content-Length','0'));body=json.loads(self.rfile.read(n).decode() if n else '{}')
    if p=='/api/auth/login':
      return self._j(200,{'ok':True,'data':{'token':TOKEN,'user':{'name':'admin'}}}) if body.get('username') and body.get('password') else self._j(401,{'ok':False})
    if p=='/api/control/execute':
      if not self._a(): return self._j(401,{'ok':False})
      return self._j(200,{'ok':True,'data':{'ticket':body.get('ticket','CTRL-001'),'status':'EXECUTED'}})
    self.send_error(404)
if __name__=='__main__':
  port=int(os.environ.get('APP_PORT','8010'));ThreadingHTTPServer(('127.0.0.1',port),H).serve_forever()
