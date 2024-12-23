from song import Song
from player import Player
import vlc

if __name__ == "__main__":
    playlist = [
        Song(mp3_file_path="../mp3/one_only.mp3", crossfade_duration=5, start_time=100, end_time=127),
        Song(mp3_file_path="../mp3/rich_flex.mp3", start_time=142)
    ]

    my_player = Player()

    # my_player.add_song(playlist[1])

    for song in playlist:
        my_player.add_song(song)

    my_player.start()
