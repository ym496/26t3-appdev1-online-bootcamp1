from flask import Flask, render_template

app = Flask(__name__)

USER_PLAYLISTS = {
    "alex": {
        "workout": ["Eye of the Tiger", "Till I Collapse", "Harder, Better, Faster, Stronger"],
        "chill": ["Weightless", "Sunset Lover", "Melancholy Hill"]
    },
    "sam": {
        "coding": ["Resonance", "90s Flanger", "Hackers Theme"],
        "roadtrip": ["Hotel California", "Go Your Own Way", "Fast Car"]
    }
}

@app.route("/")
def hello():
    users = list(USER_PLAYLISTS.keys())
    return render_template("index.html", users=users)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/user/<username>")
def user_profile(username):
    user_key = username.lower()

    if user_key not in USER_PLAYLISTS:
        return "<h2>User not found.</h2><a href='/'>Back Home</a>", 404

    user_playlists = USER_PLAYLISTS[user_key]
    links = ""
    for playlist_name in user_playlists:
        links += f"<li><a href='/user/{user_key}/playlist/{playlist_name}'>{playlist_name.title()}</a></li>"

    return f"""
    <h1>{username.title()}'s Profile</h1>
    <p>Select a playlist:</p>
    <ul>
        {links}
    </ul>
    <br>
    <a href="/">Back to Home</a>
    """

@app.route('/user/<username>/playlist/<playlist_name>')
def show_user_playlist(username, playlist_name):
    user_key = username.lower()
    playlist_key = playlist_name.lower()

    if user_key not in USER_PLAYLISTS:
        return f"<h2>User '{username}' not found.</h2>", 404

    user_data = USER_PLAYLISTS[user_key]
    if playlist_key not in user_data:
        return f"<h2>Playlist '{playlist_name}' not found for user {username}.</h2>", 404

    tracks = user_data[playlist_key]
    list_items = ""
    for track in tracks:
        list_items += f"<li>{track}</li>"

    return f"""
    <h1>{username.title()}'s "{playlist_name.title()}" Playlist</h1>
    <ul>
        {list_items}
    </ul>
    <p>
        <a href="/user/{user_key}">Back to {username.title()}'s Profile</a> | 
        <a href="/">Home</a>
    </p>
    """

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)