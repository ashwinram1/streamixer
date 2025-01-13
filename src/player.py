import pyglet
from song import Song
from queue import Queue, Empty
from utils import RequestType
from typing import List
import os


class Player:
    def __init__(self, song_queue: List[Song]=[]):
        self.song_queue = song_queue
        self.current_song_index = 0
        self.group = pyglet.media.SourceGroup()
        self.player = pyglet.media.Player()
        self.player.queue(self.group)
        self.timer = pyglet.media.PlaybackTimer()
        self.request_queue = Queue()
        self.seek_time_queue = Queue()
        self.is_playing = False
    
    def __str__(self):
        return str([str(song) for song in self.song_queue])
    
    def _set_crossfade(self, current_song, next_song):
        this_song_snippet = current_song.start_end_audio[
            -(current_song.crossfade_duration * 1000):
        ]
        next_song_snippet = next_song.start_end_audio[
            :(current_song.crossfade_duration * 1000)
        ]
        crossfade_audio = this_song_snippet.append(
            next_song_snippet,
            crossfade=current_song.crossfade_duration*1000
        )

        # Set the file path and name of the crossfade audio file
        current_song.crossfade_audio_mp3_file_path = \
            (f"{current_song.mp3_file_dir}/crossfades/"
             f"{current_song.song_name}"
             f"_X_{next_song.song_name}.mp3")
        
        # Save the crossfade audio file
        crossfade_audio.export(current_song.crossfade_audio_mp3_file_path, format="mp3")
    
    def _load_song(self, full_mp3_file_path):
        print(full_mp3_file_path)
        pyglet_media = pyglet.media.load(full_mp3_file_path)
        os.remove(full_mp3_file_path)
        print(f"LOADED & DELETING {full_mp3_file_path}")
        return pyglet_media
    
    def _prepare_next_song(self, current_song, next_song):
        # Create the final audio for the next song
        # Adjust the start and end times of the next song as needed to accommodate
        # for the current song's crossfade, as well as the next song's crossfade
        next_song.set_final_audio(
            start_time=next_song.start_time + current_song.crossfade_duration,
            end_time=next_song.end_time - next_song.crossfade_duration
        )

        # Create and queue the crossfade audio file of this current song
        # (if this song expects a crossfade)
        crossfade_duration = 0
        if current_song.crossfade_duration > 0:
            self._set_crossfade(current_song, next_song)
            pyglet_crossfade = self._load_song(
                current_song.crossfade_audio_mp3_file_path
            )
            self.group.add(pyglet_crossfade)
            crossfade_duration = pyglet_crossfade.duration
            print("Queued current song's crossfade")

        # Queue the next song
        next_pyglet_media = self._load_song(next_song.get_full_mp3_file_path())
        self.group.add(next_pyglet_media)
        print("Queued next song")

        return crossfade_duration, next_pyglet_media

    def _start(self):
        # Initial set up for first song in queue
        current_song = self.song_queue[self.current_song_index]
        current_song.set_final_audio(
            end_time=current_song.end_time - current_song.crossfade_duration
        )
        pyglet_media = self._load_song(
            current_song.get_full_mp3_file_path()
        )
        self.group.add(pyglet_media)
        self.timer.start()

        # Start main control loop
        while self.current_song_index < len(self.song_queue):
            current_song = self.song_queue[self.current_song_index]
            next_song = self.song_queue[self.current_song_index + 1] \
            if self.current_song_index < len(self.song_queue) - 1 else None

            self.player.play()
            self.is_playing = True
            self.timer.set_time(0)
            song_time_remaining = 10
            go_next = False
            go_prev = False
            # Play the song and wait for requests until 10 seconds remaining in
            # the song's final audio, at which point lock all requesting ability
            # (or ignore the incoming requests) and prepare for the crossfade
            # and/or the next song
            while song_time_remaining >= 10:
                song_time_remaining = pyglet_media.duration - self.timer.get_time()
                print(f"{song_time_remaining=}")
                request = None
                try:
                    print(f"Checking for request \
                          (timeout: {song_time_remaining / 2})")
                    request = self.request_queue.get(
                        timeout=(song_time_remaining / 2)
                    )
                except Empty:
                    print("Back awake")
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
                    go_next = True
                    break
                # As of now there is no way to go back to the previous song,
                # so a PREV request just rewinds to the beginning of the current
                # song
                elif request == RequestType.PREV:
                    # TODO: Modify data structures to enable going back to previous songs
                    print("PREV")
                    self.player.seek(0)
                    self.timer.set_time(0)
                    continue
                elif request == RequestType.SEEK:
                    seek_time = self.seek_time_queue.get()
                    print(f"SEEK: {seek_time}s")
                    self.player.seek(seek_time)
                    self.timer.set_time(seek_time)

            crossfade_duration = 0
            next_pyglet_media = None
            if next_song:
                crossfade_duration, next_pyglet_media = self._prepare_next_song(current_song, next_song)

                if go_next:
                    self.player.seek(pyglet_media.duration)
                    self.timer.set_time(pyglet_media.duration)

            # Continue to play out the current song and crossfade
            while (pyglet_media.duration + crossfade_duration) - self.timer.get_time() > 1:
                pass
            
            self.current_song_index += 1
            pyglet_media = next_pyglet_media

    def start(self):
        self._start()
