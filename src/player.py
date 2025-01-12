import vlc
from typing import List
from song import Song
from queue import Queue, Empty
from utils import RequestType
import threading


class Player:
    def __init__(self, first_song: Song=None):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.request_queue = Queue()
        self.seek_time_queue = Queue()
        self.is_playing = False
        self._create_crossfades()

        # For tracking the linked-list song queue
        self.num_songs = 1 if first_song else 0
        self.head = first_song
        self.tail = first_song
        self.current_song = None
    
    def __str__(self):
        curr = self.head
        out = []
        while curr:
            out.append(f"[{str(curr)}]")
            curr = curr.next_song
        return ' -> '.join(out)

    def _create_crossfades(self):
        # Spawn len(song_queue) - 1 number of threads, where each thread will make the crossfade
        # between its assigned song and the next song in the queue
        pass

    def add_song(self, song: Song):
        if not self.head:
            self.head = song
            self.tail = song
        else:
            song.prev_song = self.tail
            self.tail.set_next_song(song)
            self.tail = song
        self.head.prev_song = None
        self.tail.next_song = None
        self.num_songs += 1

    def remove_song(self, song: Song):
        if self.head == song:
            self.head = song.next_song
            if not self.head:
                self.tail = None
            else:
                self.head.prev_song = None
        elif self.tail == song:
            self.tail = song.prev_song
            self.tail.next_song = None
        else:
            prev_song = song.prev_song
            next_song = song.next_song
            prev_song.next_song = next_song
            next_song.prev_song = prev_song
        song.prev_song = None
        song.next_song = None
        self.num_songs -= 1

    def insert_song(self, song: Song):
        song.prev_song = self.current_song
        song.next_song = self.current_song.next_song
        self.current_song.next_song = song
        self.current_song.next_song.prev_song = song

    def _play_song(self, mp3_file_path: str):
        media = self.instance.media_new(mp3_file_path)
        self.player.set_media(media)
        self.player.play()
        self.is_playing = True
        print(f"Playing: {mp3_file_path}")

    def _start(self):
        self.current_song = self.head
        while self.current_song:
            # Ideally, we spawn a thread here to go create and insert the crossfade rather
            # than creating the crossfade when the songs are added and rather than
            # doing the insert serially here
            if self.current_song.crossfade_audio_mp3_file_path:
                self.insert_song(Song(self.current_song.crossfade_audio_mp3_file_path))
            self._play_song(self.current_song.get_full_mp3_file_path())
            song_time_remaining = 1
            go_prev = False
            while song_time_remaining >= 1:
                while (self.player.get_state() != vlc.State.Playing
                       and self._get_position() == 0.0):
                    pass
                song_time_remaining = self._get_duration() \
                    - self._get_position()
                print(f"{song_time_remaining=}")
                request = None
                try:
                    print(f"Checking for request \
                          (timeout: {song_time_remaining / 2})")
                    request = self.request_queue.get(
                        timeout=(song_time_remaining / 2)
                    )
                except Empty:
                    print("Timeout: Back awake")
                    continue
                if request == RequestType.PAUSE_PLAY:
                    print("PAUSE/PLAY")
                    self.is_playing = not self.is_playing
                    if self.is_playing:
                        self.player.play()
                    else:
                        self.player.pause()
                elif request == RequestType.NEXT:
                    print("NEXT")
                    self.player.stop()
                    break
                elif request == RequestType.PREV:
                    print("PREV")
                    if self._get_position() > 3:
                        self.player.set_time(0)
                    else:
                        self.player.stop()
                        go_prev = True
                        break
                elif request == RequestType.SEEK:
                    seek_time = self.seek_time_queue.get()
                    print(f"SEEK: {seek_time}s")
                    self.player.set_time(seek_time * 1000)
            
            self.current_song = self.current_song.prev_song if go_prev \
                else self.current_song.next_song

    def _get_position(self):
        return self.player.get_time() / 1000  # Convert to seconds

    def _get_duration(self):
        return self.player.get_length() / 1000

    def start(self):
        self._start()
