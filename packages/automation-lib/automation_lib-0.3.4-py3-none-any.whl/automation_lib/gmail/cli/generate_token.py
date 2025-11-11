"""
Gmail Token Generation CLI

Dieses Skript führt den Benutzer durch den Prozess der Erstellung eines
OAuth 2.0 Refresh Tokens für die Gmail API.

Anleitung:
1. Führen Sie dieses Skript aus: `python -m automation_lib.gmail.cli.generate_token`
2. Folgen Sie den Anweisungen in der Konsole.
"""

import os

from google_auth_oauthlib.flow import Flow

from automation_lib.gmail.config.gmail_config import GmailConfig

# Die Scopes müssen mit denen in gmail_helpers.py übereinstimmen
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.settings.basic",
    "https://www.googleapis.com/auth/admin.directory.user.readonly"
]

# Der Pfad, unter dem das Token gespeichert wird
TOKEN_PATH = "token.json"

def main():
    """Führt den Token-Generierungs-Flow aus."""
    print("--- Gmail Refresh Token Generator ---")
    
    # Lade Konfiguration, um Client ID und Secret zu erhalten
    try:
        config = GmailConfig()
        if not config.gmail_api_client_id or not config.gmail_api_client_secret:
            print("\nFehler: GMAIL_API_CLIENT_ID und GMAIL_API_CLIENT_SECRET müssen in Ihrer .env-Datei gesetzt sein.")
            print("Bitte erstellen Sie OAuth 2.0-Anmeldedaten (Typ 'Desktop-App') in der Google Cloud Console und fügen Sie die Werte hinzu.")
            return
    except Exception as e:
        print(f"\nFehler beim Laden der Konfiguration: {e}")
        print("Stellen Sie sicher, dass eine gültige .env-Datei vorhanden ist oder die Umgebungsvariablen gesetzt sind.")
        return

    client_config = {
        "installed": {
            "client_id": config.gmail_api_client_id,
            "client_secret": config.gmail_api_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"]
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob' # Out-of-band for copy-paste flow
    )

    # Erstelle die Autorisierungs-URL
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')

    print("\n1. Bitte öffnen Sie die folgende URL in Ihrem Browser:")
    print(f"\n   {auth_url}\n")
    print("2. Melden Sie sich in Ihrem Google-Konto an und erteilen Sie die Berechtigung.")
    print("3. Kopieren Sie den Autorisierungscode, der nach der Zustimmung angezeigt wird.")
    
    # Fordere den Benutzer auf, den Code einzufügen
    auth_code = input("\n4. Fügen Sie den Autorisierungscode hier ein und drücken Sie Enter: ").strip()

    if not auth_code:
        print("\nVorgang abgebrochen. Es wurde kein Code eingegeben.")
        return

    try:
        # Tausche den Code gegen Credentials (inkl. Refresh Token)
        flow.fetch_token(code=auth_code)
        creds = flow.credentials

        # Speichere die Credentials in token.json
        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())
        
        print("\n--- Erfolg! ---")
        print(f"Die Anmeldedaten wurden erfolgreich in '{os.path.abspath(TOKEN_PATH)}' gespeichert.")
        print("Das Refresh Token lautet (nur zur Information, es ist bereits gespeichert):")
        print(f"   {creds.refresh_token}")
        print("\nDas Modul ist jetzt bereit zur Verwendung mit OAuth 2.0.")

    except Exception as e:
        print(f"\nEin Fehler ist aufgetreten: {e}")
        print("Stellen Sie sicher, dass der Autorisierungscode korrekt kopiert wurde und noch gültig ist.")

if __name__ == "__main__":
    main()
