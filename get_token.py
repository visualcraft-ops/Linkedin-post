"""LinkedIn OAuth Token Generator - Run this and click the URL that opens."""
import os
import http.server
import urllib.parse
import requests
import webbrowser
import threading
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CLIENT_ID = os.environ.get("LINKEDIN_CLIENT_ID", "861hiu1qozbnqu")
CLIENT_SECRET = os.environ.get("LINKEDIN_CLIENT_SECRET", "")
REDIRECT_URI = "http://localhost:8080/callback"
SCOPES = "openid profile w_member_social"

AUTH_URL = f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={CLIENT_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}&scope={urllib.parse.quote(SCOPES)}"


class OAuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            code = params["code"][0]
            print(f"\n✅ Got authorization code!")
            print("🔄 Exchanging for access token...")

            # Exchange code for token
            resp = requests.post("https://www.linkedin.com/oauth/v2/accessToken", data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
            }, verify=False)

            if resp.ok:
                token_data = resp.json()
                access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", "unknown")

                print("\n" + "=" * 60)
                print("🎉 SUCCESS! Here's your LinkedIn Access Token:")
                print("=" * 60)
                print(f"\n{access_token}\n")
                print(f"⏰ Expires in: {int(expires_in)//86400} days")
                print("=" * 60)
                print("\n📋 Add this as LINKEDIN_TOKEN in GitHub Secrets:")
                print("https://github.com/visualcraft-ops/Linkedin-post/settings/secrets/actions")

                # Save to file
                with open("linkedin_token.txt", "w") as f:
                    f.write(access_token)
                print("\n💾 Token also saved to: linkedin_token.txt")

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Success! Token generated.</h1><p>Check your terminal. You can close this tab.</p></body></html>")
            else:
                print(f"\n❌ Error: {resp.status_code} - {resp.text}")
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(f"<html><body><h1>Error</h1><p>{resp.text}</p></body></html>".encode())

            # Shutdown server after handling
            threading.Thread(target=self.server.shutdown).start()
        else:
            self.send_response(400)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress logs


def main():
    print("=" * 60)
    print("🔐 LinkedIn OAuth Token Generator")
    print("=" * 60)
    print("\n1. Starting local server on port 8080...")

    server = http.server.HTTPServer(("localhost", 8080), OAuthHandler)

    print("2. Opening LinkedIn authorization page in browser...")
    print("3. Click 'Allow' when prompted.\n")

    webbrowser.open(AUTH_URL)

    print("⏳ Waiting for authorization... (click Allow in browser)\n")
    server.serve_forever()
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
