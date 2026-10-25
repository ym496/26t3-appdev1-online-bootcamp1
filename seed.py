"""
Seed script to populate the database with sample users, artists, songs, and playlists.

Usage:
    python seed.py
    python seed.py --keep-existing  (to avoid clearing existing records)
"""

import sys
from application.models import db, User, Song, Playlist, PlaylistSong
from main import app  

def seed_database(clear_existing=True):
    with app.app_context():
        # Ensure tables are created
        db.create_all()

        if clear_existing:
            print("Clearing existing data...")
            PlaylistSong.query.delete()
            Playlist.query.delete()
            Song.query.delete()
            User.query.delete()
            db.session.commit()
            print("Existing data cleared.")

        print("Seeding database...")

        # 1. Create Users
        users = [
            User(username="admin", password="admin", role="admin"),
            User(username="alex", password="1234", role="listener"),
            User(username="sam", password="1234", role="listener"),
            User(username="taylor", password="1234", role="artist"),
            User(username="edsheeran", password="1234", role="artist"),
            User(username="milesd", password="1234", role="artist"),
        ]

        # In case we aren't clearing existing data, avoid duplicate username errors
        created_users = {}
        for u in users:
            existing = User.query.filter_by(username=u.username).first()
            if not existing:
                db.session.add(u)
                db.session.flush()
                created_users[u.username] = u
            else:
                created_users[u.username] = existing

        db.session.commit()

        # 2. Create Songs for Artists
        taylor = created_users.get("taylor")
        edsheeran = created_users.get("edsheeran")
        milesd = created_users.get("milesd")

        songs_data = [
            # Taylor's songs
            {
                "title": "Blank Space",
                "genre": "Pop",
                "lyrics": "Nice to meet you, where you've been?\nI could show you incredible things...",
                "artist_id": taylor.id,
            },
            {
                "title": "Shake It Off",
                "genre": "Pop",
                "lyrics": "I stay out too late, got nothing in my brain\nThat's what people say...",
                "artist_id": taylor.id,
            },
            {
                "title": "Cruel Summer",
                "genre": "Synth-pop",
                "lyrics": "Fever dream high in the quiet of the night\nYou know that I caught it...",
                "artist_id": taylor.id,
            },
            # Ed Sheeran's songs
            {
                "title": "Shape of You",
                "genre": "Pop",
                "lyrics": "The club isn't the best place to find a lover\nSo the bar is where I go...",
                "artist_id": edsheeran.id,
            },
            {
                "title": "Perfect",
                "genre": "Acoustic Pop",
                "lyrics": "I found a love for me\nOh, darling, just dive right in and follow my lead...",
                "artist_id": edsheeran.id,
            },
            # Miles's songs
            {
                "title": "So What",
                "genre": "Jazz",
                "lyrics": "[Instrumental - Jazz trumpet improvisation]",
                "artist_id": milesd.id,
            },
            {
                "title": "Blue in Green",
                "genre": "Jazz",
                "lyrics": "[Instrumental - Melancholic piano and muted trumpet]",
                "artist_id": milesd.id,
            },
        ]

        created_songs = []
        for s_data in songs_data:
            song = Song.query.filter_by(
                title=s_data["title"], artist_id=s_data["artist_id"]
            ).first()
            if not song:
                song = Song(**s_data)
                db.session.add(song)
                db.session.flush()
            created_songs.append(song)

        db.session.commit()

        # 3. Create Playlists for Listeners
        alex = created_users.get("alex")
        sam = created_users.get("sam")

        playlists_data = [
            {"name": "workout", "user_id": alex.id},
            {"name": "favorites", "user_id": alex.id},
            {"name": "chill", "user_id": sam.id},
            {"name": "roadtrip", "user_id": sam.id},
        ]

        created_playlists = {}
        for p_data in playlists_data:
            playlist = Playlist.query.filter_by(
                name=p_data["name"], user_id=p_data["user_id"]
            ).first()
            if not playlist:
                playlist = Playlist(**p_data)
                db.session.add(playlist)
                db.session.flush()
            created_playlists[(p_data["user_id"], p_data["name"])] = playlist

        db.session.commit()

        # 4. Add Songs to Playlists
        # Workout playlist (Alex) -> upbeat pop
        alex_workout = created_playlists.get((alex.id, "workout"))
        alex_favs = created_playlists.get((alex.id, "favorites"))
        sam_chill = created_playlists.get((sam.id, "chill"))

        playlist_song_mappings = [
            (alex_workout.id, created_songs[0].id),  # Blank Space
            (alex_workout.id, created_songs[1].id),  # Shake It Off
            (alex_workout.id, created_songs[3].id),  # Shape of You
            (alex_favs.id, created_songs[2].id),     # Cruel Summer
            (alex_favs.id, created_songs[4].id),     # Perfect
            (sam_chill.id, created_songs[5].id),     # So What
            (sam_chill.id, created_songs[6].id),     # Blue in Green
        ]

        for playlist_id, song_id in playlist_song_mappings:
            existing_entry = PlaylistSong.query.filter_by(
                playlist_id=playlist_id, song_id=song_id
            ).first()
            if not existing_entry:
                ps = PlaylistSong(playlist_id=playlist_id, song_id=song_id)
                db.session.add(ps)

        db.session.commit()

        print("\nDatabase seeded successfully!")
        print("-" * 50)
        print("Sample Accounts Created:")
        print(f"  * Admin:     username: 'admin'     | password: 'admin'")
        print(f"  * Listener:  username: 'alex'      | password: 'password123'")
        print(f"  * Listener:  username: 'sam'       | password: 'password123'")
        print(f"  * Artist:    username: 'taylor'    | password: 'password123'")
        print(f"  * Artist:    username: 'edsheeran' | password: 'password123'")
        print(f"  * Artist:    username: 'milesd'    | password: 'password123'")
        print("-" * 50)
        print(f"Total Users:     {User.query.count()}")
        print(f"Total Songs:     {Song.query.count()}")
        print(f"Total Playlists: {Playlist.query.count()}")
        print(f"Total Tracks in Playlists: {PlaylistSong.query.count()}")
        print("-" * 50)


if __name__ == "__main__":
    clear = True
    if "--keep-existing" in sys.argv:
        clear = False
    seed_database(clear_existing=clear)

