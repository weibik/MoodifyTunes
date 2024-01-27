import urllib.parse
import requests
from flask import Flask, redirect, request, session, jsonify, render_template
import secrets
import os
from dotenv import load_dotenv
from datetime import datetime

secret_key = secrets.token_urlsafe(16)

app = Flask(__name__)
app.secret_key = secret_key

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://localhost:5000/callback"
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    scope = "user-read-private user-read-email"

    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": scope,
        "redirect_uri": REDIRECT_URI,
        "show_dialog": False,
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    return redirect(auth_url)


@app.route("/callback")
def callback():
    if "error" in request.args:
        return jsonify({"error": requests.args["error"]})

    if "code" in request.args:
        req_body = {
            "code": request.args["code"],
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }

        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()

        session["access_token"] = token_info["access_token"]
        session["refresh_token"] = token_info["refresh_token"]
        session["expires_at"] = datetime.now().timestamp() + token_info["expires_in"]

        # return redirect("/playlists")
        return redirect("/playlists_tracks")


@app.route("/playlists")
def get_playlists():
    if "access_token" not in session:
        return redirect("/login")

    if datetime.now().timestamp() > session["expires_at"]:
        return redirect("/refresh-token")

    headers = {"Authorization": f"Bearer {session['access_token']}"}

    response = requests.get(API_BASE_URL + "me/playlists", headers=headers)

    playlists_data = response.json()
    playlists_info = [
        {
            "id": playlist["id"],
            'name': playlist['name'],
            'image_url': playlist['images'][0]['url'] if playlist['images'] else None
        }
        for playlist in playlists_data.get('items', [])
    ]

    return render_template("playlists.html", playlists_info=playlists_info)


@app.route("/playlists_tracks")
def get_playlist_tracks():
    if "access_token" not in session:
        return redirect("/login")

    if datetime.now().timestamp() > session["expires_at"]:
        return redirect("/refresh-token")

    headers = {"Authorization": f"Bearer {session['access_token']}"}

    response = requests.get(API_BASE_URL + "playlists/7l9d5YLAdIHhe7rnM1TLOJ/tracks", headers=headers)

    tracks_data = response.json()
    tracks_info = [
        {
            'name': track['track']['name'],
            'artist': ', '.join([artist['name'] for artist in track['track']['artists']])
        }
        for track in tracks_data.get('items', [])
    ]

    return tracks_info


@app.route("/refresh-token")
def refresh_token():
    if "refresh_token" not in session:
        return redirect("/login")

    if datetime.now().timestamp() > session["expires_at"]:
        req_body = {
            "grant_type": "refresh_token",
            "refresh_token": session["refresh_token"],
            "client": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()

        session["access_token"] = new_token_info["access_token"]
        session["expires_at"] = (
            datetime.now().timestamp() + new_token_info["expires_in"]
        )

        return redirect("/playlists")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
