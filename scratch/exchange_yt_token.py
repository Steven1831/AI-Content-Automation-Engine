import pickle
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/youtube']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'youtube_token.pickle'

# El nuevo código que el usuario me pase
import sys
if len(sys.argv) < 2:
    print("USO: python exchange.py <CODIGO>")
    exit(1)

AUTH_CODE = sys.argv[1]

# Usamos la URI manual
flow = InstalledAppFlow.from_client_secrets_file(
    CREDENTIALS_FILE, 
    scopes=SCOPES,
    redirect_uri='urn:ietf:wg:oauth:2.0:oob'
)

# Intercambiamos el código por los tokens
flow.fetch_token(code=AUTH_CODE)
creds = flow.credentials

# Guardamos el pickle
with open(TOKEN_FILE, 'wb') as token:
    pickle.dump(creds, token)

print(f"SUCCESS: Token guardado en {TOKEN_FILE}")
