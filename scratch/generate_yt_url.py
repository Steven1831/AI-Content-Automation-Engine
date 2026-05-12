import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CREDENTIALS_FILE = 'credentials.json'

if not os.path.exists(CREDENTIALS_FILE):
    print("ERROR: No se encontró credentials.json")
    exit(1)

# Probamos con la URI especial de "fuera de banda" (Out of Band)
flow = InstalledAppFlow.from_client_secrets_file(
    CREDENTIALS_FILE, 
    scopes=SCOPES,
    redirect_uri='urn:ietf:wg:oauth:2.0:oob'
)

auth_url, _ = flow.authorization_url(
    access_type='offline',
    include_granted_scopes='true',
    prompt='consent'
)

print("\n" + "="*60)
print("PASO 1: Abre este enlace en tu dispositivo:")
print(f"\n{auth_url}\n")
print("PASO 2: Autoriza y copia el CÓDIGO que te dará Google directamente en pantalla.")
print("="*60 + "\n")
