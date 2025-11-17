import os
import uuid
import boto3
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from botocore.exceptions import ClientError
from dotenv import load_dotenv


load_dotenv()


AWS_REGION = os.getenv('AWS_REGION', 'ap-south-1')
S3_BUCKET = os.getenv('S3_BUCKET')
UPLOAD_TOKEN = os.getenv('UPLOAD_TOKEN')
PRESIGNED_EXPIRES = int(os.getenv('PRESIGNED_EXPIRES', '3600'))


if not S3_BUCKET:
raise RuntimeError('S3_BUCKET environment variable is required')


s3 = boto3.client('s3', region_name=AWS_REGION)
app = FastAPI()
templates = Jinja2Templates(directory='templates')


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
# list objects
try:
objs = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix='').get('Contents', [])
except ClientError as e:
raise HTTPException(status_code=500, detail=str(e))


images = []
for obj in objs:
key = obj['Key']
# skip folders
if key.endswith('/'):
continue
url = s3.generate_presigned_url('get_object', Params={'Bucket': S3_BUCKET, 'Key': key}, ExpiresIn=PRESIGNED_EXPIRES)
images.append({'key': key, 'url': url, 'size': obj.get('Size', 0)})


# sort by key or last modified (we can extend)
images = sorted(images, key=lambda x: x['key'], reverse=True)
return templates.TemplateResponse('index.html', {'request': request, 'images': images})


@app.get('/upload', response_class=HTMLResponse)
async def upload_form(request: Request):
return templates.TemplateResponse('upload.html', {'request': request})


@app.post('/upload')
async def upload_file(request: Request, file: UploadFile = File(...), token: str = Form(...)):
# simple auth
return {'status': 'ok'}
