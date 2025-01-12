from __future__ import annotations
from pydub import AudioSegment
import os
import glob


class Song:
    def __init__(self, mp3_file_path: str, start_time: int=-1,
                 end_time: int=-1, crossfade_duration: int=0,
                 next_song: Song=None, prev_song: Song=None):
        self.set_file_components(mp3_file_path)
        self.full_audio = AudioSegment.from_mp3(mp3_file_path)
        self.start_time = start_time if start_time > 0 else 0
        self.end_time = end_time if end_time > 0 \
            else self.full_audio.duration_seconds
        self.set_final_audio()
        # The amount of crossfade between this song and the next
        self.crossfade_duration = crossfade_duration
        self.crossfade_audio_mp3_file_path = None
        self.crossfade_audio = None
        self.prev_song = prev_song
        self.set_next_song(next_song)

    def set_file_components(self, mp3_file_path):
        components = mp3_file_path.split('/')
        self.mp3_file_dir = '/'.join(components[:-1])
        self.song_name = components[-1].split('.')[0]

    def set_final_audio(self, start_time=-1, end_time=-1):
        if start_time < 0:
            start_time = self.start_time
        if end_time < 0:
            end_time = self.end_time
        self.final_audio = self.full_audio[
            start_time * 1000:
            end_time * 1000
        ]
        self.final_audio.export(self.get_full_mp3_file_path(),
                                format="mp3")
        print(f"Final audio set for {self.song_name}: {self.get_full_mp3_file_path()}")

    def set_next_song(self, next_song: Song, crossfade: bool=True):
        self.next_song = next_song
        if self.next_song and crossfade and self.crossfade_duration > 0:
            self.set_crossfade()

    def set_crossfade(self):
        this_song_snippet = self.final_audio[
            -(self.crossfade_duration * 1000):
        ]
        next_song_snippet = self.next_song.final_audio[
            :(self.crossfade_duration * 1000)
        ]
        self.crossfade_audio = this_song_snippet.append(
            next_song_snippet,
            crossfade=self.crossfade_duration*1000
        )
        self.crossfade_audio_mp3_file_path = \
            (f"../mp3/crossfades/{self.get_song_names_with_time_stamps()}"
             f"_X_{self.next_song.get_song_names_with_time_stamps()}.mp3")
        self.crossfade_audio.export(self.crossfade_audio_mp3_file_path,
                                    format="mp3")
        self.set_final_audio(end_time=self.end_time - self.crossfade_duration)
        self.next_song.set_final_audio(
            start_time=self.next_song.start_time + self.crossfade_duration
        )

    def get_song_names_with_time_stamps(self):
        return f"{self.song_name}_{self.start_time}_{self.end_time}"

    def get_full_mp3_file_path(self):
        return (f"{self.mp3_file_dir}/{self.song_name}"
                f"_{self.start_time}_{self.end_time}.mp3")

    def _delete_irrelevant_final_audio(self):
        for f in glob.glob(f"{self.mp3_file_dir}/{self.song_name}_*.mp3"):
            if f != self.get_full_mp3_file_path():
                print(f"Deleting: {f}")
                os.remove(f)

    def __str__(self):
        return (f"{self.song_name} | "
                f"Start: {self.start_time}s | End: {self.end_time}s")
