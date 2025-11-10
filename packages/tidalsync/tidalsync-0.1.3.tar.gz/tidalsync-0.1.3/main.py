import tidalapi
from time import sleep


def main():
    print("Linking with old account...")
    old = tidalapi.Session()
    old.login_oauth_simple()
    print("Linking with new account...")
    new = tidalapi.Session()
    new.login_oauth_simple()

    failures = []

    for album in tidalapi.Favorites(old, old.user.id).albums():
        try:
            print("Syncing album:", album.name)
            tidalapi.Favorites(new, new.user.id).add_album(album_id=album.id)

        except Exception as e:
            print(f"Failed... 💩 {e}")
            failures.append(["album", album])
    for artist in tidalapi.Favorites(old, old.user.id).artists():
        try:
            print("Syncing artist:", artist.name)
            tidalapi.Favorites(new, new.user.id).add_artist(artist_id=artist.id)
        except Exception as e:
            print(f"Failed... 💩 {e}")
            failures.append(["artist", artist])
    for track in tidalapi.Favorites(old, old.user.id).tracks():
        try:
            print("Syncing track:", track.name)
            tidalapi.Favorites(new, new.user.id).add_track(track_id=track.id)
        except Exception as e:
            print(f"Failed... 💩 {e}")
            failures.append(["track", track])

    playlists = old.user.playlists()

    for playlist in playlists:
        print("Creating " + playlist.name)
        new_playlist = new.user.create_playlist(playlist.name, "")
        tracks_to_add = [x.id for x in playlist.tracks()]
        if tracks_to_add:
            print("Adding tracks to new playlist " + playlist.name)
            new_playlist.add(tracks_to_add)
        else:
            print(f"Playlist {playlist.name} has no tracks, skipping adding tracks.")
        sleep(3)

    print("\n☯ Done syncing everything.")
    if failures:
        print("Total failures: ", str(len(failures)))
        for failure in failures:
            print("FAIL: ", failure[0], "-", failure[1].name)


if __name__ == "__main__":
    main()
