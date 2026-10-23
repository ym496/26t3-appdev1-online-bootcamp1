from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///beatbox.db'
db = SQLAlchemy(app)

# models

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(12), unique=True, nullable=False)
    password = db.Column(db.String(12), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='listener')

class Song(db.Model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=True)
    lyrics = db.Column(db.Text, nullable=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Playlist(db.Model):
    __tablename__ = 'playlists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class PlaylistSong(db.Model):
    __tablename__ = 'playlist_songs'
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)


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
def user_profile(username):
    user_key = username.lower()
    user = User.query.filter_by(username=user_key).first()
    if not user:
        return "<h2>User not found.</h2>", 404

    playlists = Playlist.query.filter_by(user_id=user.id).all()

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
    user = User.query.filter_by(username=user_key).first()
    if user is None:
        return "<h2>User not found.</h2>", 404

    playlist = Playlist.query.filter_by(name=playlist_key, user_id=user.id).first()
    if playlist is None:
        return f"<h2>Playlist '{playlist_name}' not found.</h2>", 404

    tracks = PlaylistSong.query.filter_by(playlist_id=playlist.id).all()

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
        if user and user.password == password:
            if user.role == 'artist':
                return redirect(url_for('artist_profile', username=user_key))
            else:
                return redirect(url_for('user_profile', username=user_key))
        else:
            return "Invalid username or password. Please try again."    
            
    return render_template("login.html")

@app.route('/logout')
def logout():
    return redirect(url_for('hello'))


def init_db():
    with app.app_context():
        db.create_all()
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', password='admin', role='admin')
            db.session.add(admin_user)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=True)