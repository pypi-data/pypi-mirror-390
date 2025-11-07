import json

import requests
from brainframe_apps.domain_defs import KC_TOKEN_EP
from brainframe_apps.logger_factory import log


def domain_signin(base_url, client_id, username, password, cert=None):

    token_endpoint = f"{base_url}/{KC_TOKEN_EP}"

    token_data = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "scope": "openid",
    }

    if client_id is not None:
        token_data["client_id"] = client_id

    response = requests.post(token_endpoint, data=token_data, verify=cert)
    if response.status_code == 200:
        response_json = json.loads(response.text)
        access_token = response_json["access_token"]
        refresh_token = response_json["refresh_token"]
        log.debug(f"{username} authorized by domain {base_url}")
        return access_token, refresh_token
    else:
        log.debug(
            f"domain_signin authorization error {response.status_code} by {token_endpoint}: {response.text}"
        )
        return None, None
