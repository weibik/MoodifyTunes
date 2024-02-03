import urllib.parse
import requests
from flask import Flask, redirect, request, session, jsonify, render_template
import secrets
import os
from dotenv import load_dotenv
from datetime import datetime
from tracks_rules import classify_track

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

        return redirect("/playlists")


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
            "name": playlist["name"],
            "image_url": playlist["images"][0]["url"] if playlist["images"] else None,
        }
        for playlist in playlists_data.get("items", [])
    ]
    playlists_info_sorted = sorted(playlists_info, key=lambda x: x["name"])

    return render_template("playlists.html", playlists_info=playlists_info_sorted)


@app.route("/playlists/<string:playlist_id>/tracks")
def get_playlist_tracks(playlist_id):
    if "access_token" not in session:
        return redirect("/login")

    if datetime.now().timestamp() > session["expires_at"]:
        return redirect("/refresh-token")

    headers = {"Authorization": f"Bearer {session['access_token']}"}

    response = requests.get(
        API_BASE_URL + f"playlists/{playlist_id}/tracks", headers=headers
    )

    tracks_data = response.json()
    tracks_info = [
        {
            "id": track["track"]["id"],
            "name": track["track"]["name"],
            "artist": ", ".join(
                [artist["name"] for artist in track["track"]["artists"]]
            ),
        }
        for track in tracks_data.get("items", [])
    ]

    return render_template("tracks.html", tracks_info=tracks_info)


@app.route("/audio-features/<string:track_id>")
def get_track_feature(track_id):
    if "access_token" not in session:
        return redirect("/login")

    if datetime.now().timestamp() > session["expires_at"]:
        return redirect("/refresh-token")

    headers = {"Authorization": f"Bearer {session['access_token']}"}

    response = requests.get(
        API_BASE_URL + f"audio-features/{track_id}", headers=headers
    )

    track_data = response.json()

    track_features = {
        "acousticness": track_data["acousticness"],
        "danceability": track_data["danceability"],
        "energy": track_data["energy"],
        "instrumentalness": track_data["instrumentalness"],
        "valence": track_data["valence"],
        "liveness": track_data["liveness"],
    }
    track_type = classify_track(track_features)
    return render_template("track_features.html", track=track_features, track_type=track_type)


@app.route("/refresh-token")
def refresh_token():
    if "refresh_token" not in session:
        return redirect("/login")

    if datetime.now().timestamp() > session["expires_at"]:
        req_body = {
            "grant_type": "refresh_token",
            "refresh_token": session["refresh_token"],
            "client_id": CLIENT_ID,
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
