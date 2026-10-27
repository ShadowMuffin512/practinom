import flet_audio

import consts

METRONOME_SAMPLES = {
    consts.SoundLibrary.NORMAL: {
        consts.BeatType.BEAT: "metronome-tick.mp3",
        consts.BeatType.MEASURE: "metronome-tick-start.mp3",
        consts.BeatType.STEP: "metronome-step.mp3",
    }
}


class AudioPlayer:
    def __init__(
        self,
        volume: float = 1.0,
        library: consts.SoundLibrary = consts.SoundLibrary.NORMAL,
    ):
        self.volume = volume
        self.current_library = library
        self.players: dict[consts.BeatType, flet_audio.Audio] = {
            beat_type: flet_audio.Audio(
                src=src,
                volume=self.volume,
                release_mode=flet_audio.ReleaseMode.STOP,
            )
            for beat_type, src in METRONOME_SAMPLES[self.current_library].items()
        }

    @property
    def audio_sample(self) -> flet_audio.Audio:
        return self.players[consts.BeatType.BEAT]

    def get_services(self) -> list[flet_audio.Audio]:
        return list(self.players.values())

    def set_sound_library(self, library: consts.SoundLibrary):
        self.current_library = library
        for beat_type, src in METRONOME_SAMPLES[library].items():
            if beat_type in self.players:
                self.players[beat_type].src = src

    async def play_metronome_sound(self, beat_type: consts.BeatType):
        player = self.players.get(beat_type)
        if player:
            await player.play()
