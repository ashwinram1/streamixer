from __future__ import annotations
from pydub import AudioSegment


class Song:
    def __init__(self, mp3_file_path: str, start_time: int=-1,
                 end_time: int=-1, crossfade_duration: int=0):
        self.set_file_components(mp3_file_path)
        self.full_audio = AudioSegment.from_mp3(mp3_file_path)  # pydub array that represents the whole given .mp3
        self.start_time = start_time if start_time > 0 else 0
        self.end_time = end_time if end_time > 0 \
            else self.full_audio.duration_seconds
        self.start_end_audio = self.full_audio[  # pydub array that represents the custom entry/exit point
            self.start_time * 1000:
            self.end_time * 1000
        ]
        self.crossfade_duration = crossfade_duration  # The amount of crossfade between this song and the next
        self.crossfade_audio_mp3_file_path = None

    def set_file_components(self, mp3_file_path):
        components = mp3_file_path.split('/')
        self.mp3_file_dir = '/'.join(components[:-1])
        self.song_name = components[-1].split('.')[0]

    def set_final_audio(self, start_time=-1, end_time=-1, save=True):
        start_time = self.start_time if start_time < 0 else start_time
        end_time = self.end_time if end_time < 0 else end_time
        self.final_audio = self.full_audio[  # pydub array that represents the audio that will actually be played
            start_time * 1000:
            end_time * 1000
        ]
        print(f"Final audio SET for {self.song_name}: {self.get_full_mp3_file_path()}")
        if save:
            self.final_audio.export(self.get_full_mp3_file_path(),
                                    format="mp3")
            print(f"Final audio SAVED for {self.song_name}: {self.get_full_mp3_file_path()}")

    def get_full_mp3_file_path(self):
        return (f"{self.mp3_file_dir}/{self.song_name}_temp.mp3")

    def __str__(self):
        return (f"{self.song_name} | "
                f"Start: {self.start_time}s | End: {self.end_time}s")
