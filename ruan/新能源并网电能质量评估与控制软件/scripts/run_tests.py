from __future__ import annotations
import os, subprocess, sys, time, json
from urllib.request import Request, urlopen
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE='http://127.0.0.1:8010'
proc=subprocess.Popen([sys.executable,'apps/api/main.py'],cwd=ROOT,env={**os.environ,'APP_PORT':'8010'})
try:
  time.sleep(1)
  req=Request(BASE+'/api/auth/login',data=json.dumps({'username':'admin','password':'admin123'}).encode(),method='POST');req.add_header('Content-Type','application/json')
  tok=json.loads(urlopen(req,timeout=3).read().decode())['data']['token']
  req2=Request(BASE+'/api/dashboard');req2.add_header('Authorization','Bearer '+tok)
  urlopen(req2,timeout=3)
  print('tests passed')
finally:
  proc.terminate();proc.wait(timeout=5)
