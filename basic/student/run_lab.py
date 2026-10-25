from pathlib import Path
import argparse,os
parser=argparse.ArgumentParser()
parser.add_argument('--mode',choices=['ready','slow','empty','error','invalid'],default='ready')
parser.add_argument('--port',type=int,default=8000)
args=parser.parse_args()
os.environ['PM_FRONTEND_MODE']=args.mode
import uvicorn
uvicorn.run('api_app:app',host='127.0.0.1',port=args.port,app_dir=str(Path(__file__).resolve().parent))
