from song import Song
from player import Player
import vlc

if __name__ == "__main__":
    playlist = [
        Song(mp3_file_path="../mp3/members_only.mp3", crossfade_duration=5, start_time=90, end_time=110),
        Song(mp3_file_path="../mp3/balloons.mp3", start_time=10)
    ]

    my_player = Player()

    # my_player.add_song(playlist[1])

    for song in playlist:
        my_player.add_song(song)

    print(my_player)

    my_player.start()
