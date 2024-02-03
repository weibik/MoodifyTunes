def classify_track(track_features):
    energetic_rule = track_features['energy'] > 0.7 and track_features['tempo'] > 120 and track_features['danceability'] > 0.6
    happy_rule = track_features['valence'] > 0.7 and track_features['energy'] > 0.5 and track_features['danceability'] > 0.5
    sad_rule = track_features['valence'] < 0.4 < track_features['acousticness'] and track_features['energy'] < 0.5
    acoustic_vibes_rule = track_features['acousticness'] > 0.6 and track_features['instrumentalness'] > 0.5 and track_features['liveness'] < 0.3
    chill_rule = track_features['valence'] < 0.6 and track_features['energy'] < 0.6 and track_features['tempo'] < 100
    live_sessions_rule = track_features['liveness'] > 0.5 and track_features['instrumentalness'] < 0.3

    if energetic_rule:
        return "Energetic Playlist"
    elif happy_rule:
        return "Happy/Upbeat Playlist"
    elif sad_rule:
        return "Sad/Reflective Playlist"
    elif acoustic_vibes_rule:
        return "Acoustic Vibes Playlist"
    elif chill_rule:
        return "Chill/Laid-back Playlist"
    elif live_sessions_rule:
        return "Live Sessions Playlist"
    else:
        return "Eclectic Mix Playlist"

# Example track features
track_features = {
    "acousticness": 0.293,
    "danceability": 0.593,
    "energy": 0.503,
    "instrumentalness": 0,
    "liveness": 0.405,
    "valence": 0.71,
    # Add other features as needed
}

# Classify the track
playlist_category = classify_track(track_features)
print(f"The track belongs to the '{playlist_category}' playlist.")
