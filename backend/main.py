import os
import json
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse
from dotenv import load_dotenv
import services
import models  # Ensure tables are created on import

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Middleware for sessions
app.add_middleware(SessionMiddleware, secret_key=os.getenv('SECRET_KEY'))

# Load Auth0 configuration from environment variables
auth_config = {
    'domain': os.getenv('AUTH0_DOMAIN'),
    'clientId': os.getenv('AUTH0_CLIENT_ID'),
    'clientSecret': os.getenv('AUTH0_CLIENT_SECRET'),
    'audience': os.getenv('AUTH0_AUDIENCE')
}

oauth = OAuth()
oauth.register(
    name='auth0',
    client_id=auth_config['clientId'],
    client_secret=auth_config['clientSecret'],
    authorize_url=f"https://{auth_config['domain']}/authorize",
    authorize_params=None,
    access_token_url=f"https://{auth_config['domain']}/oauth/token",
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri='http://localhost:8000/callback',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{auth_config['domain']}/authorize",
    tokenUrl=f"https://{auth_config['domain']}/oauth/token"
)

# Routes
@app.get('/')
async def home():
    return JSONResponse({'message': 'Welcome to the FastAPI + Auth0 Integration Example!'})

@app.route('/login')
async def login(request: Request):
    redirect_uri = 'http://localhost:8000/callback'
    return await oauth.auth0.authorize_redirect(request, redirect_uri)

@app.route('/callback')
async def auth(request: Request):
    token = await oauth.auth0.authorize_access_token(request)
    user = await oauth.auth0.parse_id_token(request, token)
    request.session['user'] = dict(user)
    return RedirectResponse(url='/dashboard')

@app.route('/dashboard')
async def dashboard(request: Request):
    user = request.session.get('user')
    if user:
        return JSONResponse({'message': 'You are logged in', 'user': user})
    return RedirectResponse(url='/')

@app.get('/users')
async def get_users(token: str = Depends(oauth2_scheme)):
    users = services.get_users()
    return users

@app.post('/users')
async def insert_user(name: str, email: str, token: str = Depends(oauth2_scheme)):
    services.insert_user(name, email)
    return {"message": "User added successfully"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)