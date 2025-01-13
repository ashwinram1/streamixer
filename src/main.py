from song import Song
from player import Player
import threading
from utils import RequestType
import time


if __name__ == "__main__":
    # Example song queue/playlist for testing
    playlist = [
        Song(mp3_file_path="../mp3/members_only.mp3", crossfade_duration=2, start_time=90, end_time=110),
        Song(mp3_file_path="../mp3/balloons.mp3", crossfade_duration=2, start_time=10, end_time=20),
        Song(mp3_file_path="../mp3/members_only.mp3", crossfade_duration=2, start_time=90, end_time=110),
        Song(mp3_file_path="../mp3/balloons.mp3", crossfade_duration=2, start_time=10, end_time=20),
        Song(mp3_file_path="../mp3/members_only.mp3", start_time=90, end_time=110)
    ]

    my_player = Player(song_queue=playlist)

    print(my_player)

    my_player.start()
