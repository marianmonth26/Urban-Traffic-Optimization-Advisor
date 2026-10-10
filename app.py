from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import json
from agents import analyze
ROOT=Path(__file__).resolve().parent
class Handler(BaseHTTPRequestHandler):
    def send(self,status,body,mime):
        self.send_response(status);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(body)));self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(body)
    def do_GET(self):
        files={'/':('index.html','text/html; charset=utf-8'),'/sample':('sample.csv','text/plain'),'/main.js':('main.js','text/javascript'),'/style.css':('style.css','text/css')}
        if self.path not in files:return self.send(404,b'Not found','text/plain')
        file,mime=files[self.path];self.send(200,(ROOT/file).read_bytes(),mime)
    def do_POST(self):
        if self.path!='/api/analyze':return self.send(404,b'Not found','text/plain')
        try:
            size=int(self.headers.get('Content-Length',0))
            if not 0<size<=4000000:raise ValueError('Input must be between 1 byte and 4 MB.')
            data=json.loads(self.rfile.read(size));result=analyze(data['source'],data['weather'],data['event'],data['cycle'])
            self.send(200,json.dumps(result).encode(),'application/json')
        except (ValueError,TypeError,KeyError,AttributeError) as e:self.send(400,json.dumps({'error':str(e)}).encode(),'application/json')
if __name__=='__main__':
    print('Joseph Traffic Advisor: http://127.0.0.1:8003/',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8003),Handler).serve_forever()

