from flask import Flask, render_template, request, redirect, url_for, session
from flask import current_app as app
from application.models import db, User, Song, Playlist, PlaylistSong
from application.decorators import admin_required, artist_required, listener_required


@app.route("/")
def hello():
    users = User.query.all()
    # [<User 1>, <User 2>, ...]
    print(users[0].password) 
    # ['alex', 'sam', 'musical']
    registered_users = [user.username for user in users]
    return render_template("index.html",registered_users=registered_users)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/user/<username>")
@listener_required
def user_profile(username):
    user_key = username.lower()
    user = User.query.filter_by(username=user_key).first()
    songs = Song.query.all()
    if not user:
        return "<h2>User not found.</h2>", 404

    playlists = Playlist.query.filter_by(user_id=user.id).all()

    return render_template(
        "user_profile.html",
        username=username,
        user_key=user_key,
        playlists=playlists,
        songs=songs
    )

@app.route("/blacklist_user/<int:user_id>", methods=["POST"])
@admin_required
def blacklist_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return "<h2>User not found.</h2>", 404
    role = user.role
    user.is_blacklisted = True
    db.session.commit()
    if role == 'artist':
        return redirect(url_for('show_artists'))
    else:
        return redirect(url_for('show_users'))

@app.route("/unblacklist_user/<int:user_id>", methods=["POST"])
def unblacklist_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return "<h2>User not found.</h2>", 404

    user.is_blacklisted = False
    role = user.role
    db.session.commit()
    if role == 'artist':
        return redirect(url_for('show_artists'))
    else:
        return redirect(url_for('show_users'))


@app.route("/users",methods=["GET"])
def show_users():
    users = User.query.all()
    return render_template("users.html", users=users)

@app.route("/artists",methods=["GET"])
def show_artists():
    users = User.query.filter_by(role="artist").all()
    return render_template("artists.html", users=users)


@app.route('/user/<username>/playlist/<playlist_name>')
def show_user_playlist(username, playlist_name):
    user_key = username.lower()
    playlist_key = playlist_name.lower()
    user = User.query.filter_by(username=user_key).first()
    if user is None:
        return "<h2>User not found.</h2>", 404

    playlist = Playlist.query.filter_by(name=playlist_key, user_id=user.id).first()
    if playlist is None:
        return f"<h2>Playlist '{playlist_name}' not found.</h2>", 404

    playlist_tracks = PlaylistSong.query.filter_by(playlist_id=playlist.id).all()
    song_ids = [track.song_id for track in playlist_tracks]
    tracks = []
    for song_id in song_ids:
        song = Song.query.filter_by(id=song_id).first()
        if song:
            tracks.append(song)
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
    playlist = Playlist.query.filter_by(name=playlist_name, user_id=User.query.filter_by(username=user_key).first().id).first()
    if playlist:
        return f"<h2>Playlist '{playlist_name}' already exists for user '{username}'.</h2>", 400
    playlist = Playlist(name=playlist_name, user_id=User.query.filter_by(username=user_key).first().id)
    db.session.add(playlist)
    db.session.commit()
    return redirect(url_for('user_profile', username=user_key))


@app.route('/artist/<username>')
@artist_required
def artist_profile(username):
    user_key = username.lower()
    user = User.query.filter_by(username=user_key).first()
    if not user:
        return "<h2>Artist not found.</h2>", 404

    songs = Song.query.filter_by(artist_id=user.id).all()

    return render_template(
        "artist_profile.html",
        username=username,
        user_key=user_key,
        songs=songs
    )

@app.route('/artist/<username>/add_song', methods=['GET', 'POST'])
def add_song(username):
    if request.method == 'POST':
        user_key = username.lower()
        user = User.query.filter_by(username=user_key).first()
        if not user:
            return "<h2>Artist not found.</h2>", 404

        song_title = request.form['song_title'].strip()
        genre = request.form['genre'].strip()
        lyrics = request.form['lyrics'].strip()

        song = Song(title=song_title, genre=genre, lyrics=lyrics, artist_id=user.id)
        db.session.add(song)
        db.session.commit()

        return redirect(url_for('artist_profile', username=user_key))
    return render_template("add_song.html", username=username)



@app.route('/delete_song/<int:song_id>', methods=['POST'])
def delete_song(song_id):
    song = Song.query.get(song_id)
    if not song:
        return "<h2>Song not found.</h2>", 404

    db.session.delete(song)
    db.session.commit()
    artist_key = User.query.get(song.artist_id).username
    return redirect(url_for('artist_profile', username=artist_key))

@app.route('/edit_song/<int:song_id>', methods=['GET', 'POST'])
def edit_song(song_id):
    song = Song.query.get(song_id)
    if not song:
        return "<h2>Song not found.</h2>", 404

    if request.method == 'POST':
        song.title = request.form['song_title'].strip()
        song.genre = request.form['genre'].strip()
        song.lyrics = request.form['lyrics'].strip()
        db.session.commit()
        artist_key = User.query.get(song.artist_id).username
        return redirect(url_for('artist_profile', username=artist_key))

    return render_template("edit_song.html", song=song, username=User.query.get(song.artist_id).username)

@app.route('/song/<int:song_id>')
def song_page(song_id):
    song = Song.query.get(song_id)
    if not song:
        return "<h2>Song not found.</h2>", 404

    artist = User.query.get(song.artist_id)

    return render_template(
        "song_page.html",
        song=song,
        artist=artist
    )


@app.route('/admin')
@admin_required
def admin_dash():
    return render_template("admin_dash.html")   

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        role = request.form['role']
        user_key = username.lower()
        user = User.query.filter_by(username=user_key).first()
        if user:
            return "Username already exists. Please choose a different username."
        user = User(username=user_key, password=password, role=role)
        db.session.add(user)
        db.session.commit()
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
        user = User.query.filter_by(username=user_key).first()
        if user and user.is_blacklisted:
            return "Your account has been blacklisted. Please contact the administrator."
        if user and user.password == password:
            session['username'] = user_key
            session['role'] = user.role
            if user.role == 'artist':
                return redirect(url_for('artist_profile', username=user_key))
            elif user.role == 'admin':
                return redirect(url_for('admin_dash'))
            else:
                return redirect(url_for('user_profile', username=user_key))
        else:
            return "Invalid username or password. Please try again."    
            
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('hello'))
