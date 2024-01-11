import base64
import json
import os
from urllib.parse import urlencode
from dotenv import load_dotenv
from requests import post, get
import webbrowser

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "client_credentials",
        "code": "AQAc1v9YJadkDlaQlLrTIqcpruqfsOitLwEZuB2eRmSMLu2ZT9YjqUo0FgRJgvbI0Z3X4TfDYT9NfQ1zIqQe-iBWTLqZ0Ni8H2wQ"
        "663-J0g3jXmi4m6cuSvhLq4ZE7wlOJ97hlgrDFbl324iebfp8WXc1ALC7MrBtDGH-IFxhpT1d7_OZauDnsaJKzxM3dSKdZNYT"
        "9lL7FE-",
        "redirect_uri": "http://localhost/",
    }

    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_code_from_web():
    auth_headers = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": "http://localhost/",
        "scope": "user-read-email user-read-private",
    }

    webbrowser.open("https://accounts.spotify.com/authorize?" + urlencode(auth_headers))


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def get_user_id(token):
    """TODO: Needs user-read-private and user-read-email to have authorization."""

    url = "https://api.spotify.com/v1/me"
    headers = get_auth_header(token)
    query_url = url
    user_params = {"limit": 50}
    result = get(query_url, params=user_params, headers=headers)
    json_result = json.loads(result.content)
    if len(json_result) == 0:
        print(f"No playlists with name {playlist_name} exits.")
        return None
    else:
        return json_result


def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query

    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print(f"No artist with name {artist_name} exits.")
        return None
    else:
        return json_result[0]


def search_for_playlist(token, playlist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f'?q="{playlist_name}"&type=playlist'
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["playlists"]["items"]
    if len(json_result) == 0:
        print(f"No playlists with name {playlist_name} exits.")
        return None
    else:
        return json_result


def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result
