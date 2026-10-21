from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

USER_PLAYLISTS = {
    "alex": {
        "workout": ["Eye of the Tiger", "Till I Collapse", "Harder, Better, Faster, Stronger"],
        "chill": ["Weightless", "Sunset Lover", "Melancholy Hill"]
    },
    "sam": {
        "coding": ["Resonance", "90s Flanger", "Hackers Theme"],
        "roadtrip": ["Hotel California", "Go Your Own Way", "Fast Car"]
    },
    "musical": {}
}

Users = {}

@app.route("/")
def hello():
    users = list(USER_PLAYLISTS.keys())
    registered_users = list(Users.keys())
    return render_template("index.html", users=users, registered_users=registered_users)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/user/<username>")
def user_profile(username):
    user_key = username.lower()

    if user_key not in USER_PLAYLISTS:
        return "<h2>User not found.</h2><a href='/'>Back Home</a>", 404

    playlists = list(USER_PLAYLISTS[user_key].keys())

    return render_template(
        "user_profile.html",
        username=username,
        user_key=user_key,
        playlists=playlists
    )

@app.route('/user/<username>/playlist/<playlist_name>')
def show_user_playlist(username, playlist_name):
    user_key = username.lower()
    playlist_key = playlist_name.lower()

    if user_key not in USER_PLAYLISTS:
        return "<h2>User not found.</h2>", 404

    user_data = USER_PLAYLISTS[user_key]
    if playlist_key not in user_data:
        return f"<h2>Playlist '{playlist_name}' not found.</h2>", 404

    tracks = user_data[playlist_key]

    return render_template(
        "user_playlist.html",
        username=username,
        user_key=user_key,
        playlist_name=playlist_name,
        tracks=tracks
    )

@app.route('/user/<username>/playlist/create', methods=['POST'])
def create_playlist(username):
    user_key = username.lower()
    playlist_name = request.form['playlist_name'].strip().lower()

    if user_key in USER_PLAYLISTS and playlist_name:
        if playlist_name not in USER_PLAYLISTS[user_key]:
            USER_PLAYLISTS[user_key][playlist_name] = []

    return redirect(url_for('user_profile', username=user_key))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user_key = username.lower()

        if user_key in Users:
            return "Username already exists. Please choose a different one."

        # 1. Register user
        Users[user_key] = password

        # 2. Create empty playlists dictionary for this user
        USER_PLAYLISTS[user_key] = {}

        # 3. Success message with a 'Log In Now' button/link
        return f"""
        <h2>User '{username}' registered successfully!</h2>
        <a href="{url_for('login')}">
            <button type="button">Log In Now</button>
        </a>
        """
        
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user_key = username.lower()

        if user_key in Users and Users[user_key] == password:
            return redirect(url_for('user_profile', username=user_key))
        else:
            return "Invalid username or password. Please try again."    
            
    return render_template("login.html")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)