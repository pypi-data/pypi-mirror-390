import base64
import hashlib
import secrets
import string
import threading
import uuid

# import socketserver
# import ssl
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Tuple
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from brainframe_apps.cognito_defs import COGNITO_AUTHORIZE_EP, COGNITO_TOKEN_EP
from brainframe_apps.logger_factory import log
from requests_oauthlib import OAuth2Session


def make_pkce_code() -> Tuple[str, str]:
    """Generates a PKCE code and returns a code challenge and code verifier. The
    code challenge is provided to Cognito when the flow starts, and the code
    verifier is provided when requesting the access and refresh tokens. These values
    are used by Cognito to ensure that it's talking to the same client throughout
    the entire flow.
    """
    alphanumeric = string.ascii_letters + string.digits
    code_verifier = "".join(secrets.choice(alphanumeric) for _ in range(128))

    code_challenge = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode().replace("=", "")

    return code_challenge, code_verifier


redirect_domain = "http://localhost"


def get_authorization_redirect_url(domain, port, client_id, scopes, code_challenge):
    authorize_url = f"https://{domain}/{COGNITO_AUTHORIZE_EP}"
    params = {
        "response_type": "code",
        "client_id": client_id,
        "scope": scopes,
        "redirect_uri": f"{redirect_domain}:{port}/",
        "state": str(uuid.uuid4()),
        "identity_provider": "COGNITO",
        "code_challenge_method": "S256",
        "code_challenge": code_challenge,
        "access_type": "offline",
    }
    authorization_redirect_url = authorize_url + "?" + urlencode(params)
    return authorization_redirect_url


authorization_code = None


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Extract the authorization code from the redirect URL
        redirect_response = self.path

        parsed_url = urlparse(redirect_response)
        query = parse_qs(parsed_url.query)
        code = query["code"][0]
        global authorization_code
        authorization_code = code

        # Display the access token
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(
            bytes(
                f"<html><body><h1>Authorization code: {code}</h1></body></html>",
                "utf-8",
            )
        )


def start_server(server_address, callback_handler):

    httpd = HTTPServer(server_address, callback_handler)

    # Create an SSL context to use for the server
    # ssl_context = ssl.SSLContext()
    # ssl_context.verify_mode = ssl.CERT_NONE

    # httpd.socket = ssl_context.wrap_socket(httpd.socket, server_side=True)

    server_thread = threading.Thread(target=httpd.handle_request)
    server_thread.start()

    return httpd, server_thread


def wait_authorization_code_from_browser(authorization_redirect_url, port, client_id):
    oauth = OAuth2Session(client_id, redirect_uri=authorization_redirect_url)

    server_address = ("", port)

    httpd, httpd_thread = start_server(server_address, CallbackHandler)

    webbrowser.open(authorization_redirect_url)

    httpd_thread.join()

    httpd.server_close()

    global authorization_code
    return authorization_code


def get_access_token(domain, port, client_id, authorization_code, code_verifier):
    access_token_url = f"https://{domain}/{COGNITO_TOKEN_EP}"
    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "code_verifier": code_verifier,
        "code": authorization_code,
        "redirect_uri": f"{redirect_domain}:{port}/",
    }

    access_token_response = requests.post(access_token_url, data=data)

    access_token = access_token_response.json()["access_token"]
    refresh_token = access_token_response.json()["refresh_token"]
    id_token = access_token_response.json()["id_token"]
    expires_in = access_token_response.json()["expires_in"]
    token_type = access_token_response.json()["token_type"]

    return access_token, refresh_token


def get_cognito_access_token(domain, port, client_id, scopes):
    code_challenge, code_verifier = make_pkce_code()

    # Step 1: Get the authorization code
    authorization_redirect_url = get_authorization_redirect_url(
        domain, port, client_id, scopes, code_challenge
    )
    authorization_code = wait_authorization_code_from_browser(
        authorization_redirect_url, port, client_id
    )

    # Step 2: Get the access token
    access_token, refresh_token = get_access_token(
        domain, port, client_id, authorization_code, code_verifier
    )

    return access_token, refresh_token


if __name__ == "__main__":
    get_cognito_access_token()
