import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from math import floor

import consts
from audio_player import AudioPlayer


@dataclass
class Metronome:
    starting_tempo: int
    ending_tempo: int
    steps: int
    measures_per_step: int
    beats: int
    audio_player: AudioPlayer | None = None
    current_step: int = 0
    current_beat_in_step: int = 0
    stopped: bool = False
    _task: asyncio.Task | None = field(default=None, init=False, repr=False)
    _listeners: list[Callable[[str, any], None]] = field(
        default_factory=list, init=False, repr=False
    )

    def add_listener(self, listener: Callable[[str, any], None]) -> None:
        self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[str, any], None]) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    @property
    def step_size(self) -> int:
        return floor((self.ending_tempo - self.starting_tempo) / self.steps)

    @property
    def current_interval_sec(self) -> float:
        return 60 / self.current_tempo

    @property
    def current_tempo(self) -> int:
        return self.starting_tempo + self.current_step * self.step_size

    async def beat(self) -> consts.BeatType:
        print(
            f"BEAT, current tempo: {self.current_tempo}, current beat in step: {self.current_beat_in_step}"
        )
        sound = consts.BeatType.BEAT
        if self.current_beat_in_step >= self.measures_per_step * self.beats:
            self.incrase_step()
            sound = consts.BeatType.STEP
        elif self.current_beat_in_step % self.beats == 0:
            sound = consts.BeatType.MEASURE
        print(sound)
        self.current_beat_in_step += 1
        if self.audio_player is not None:
            await self.audio_player.play_metronome_sound(sound)
        return sound

    def incrase_step(self) -> None:
        self.current_step += 1
        self.current_beat_in_step = 0
        if self.current_step > self.steps:
            self.stop()

    def play(self) -> asyncio.Task:
        if self._task is not None and not self._task.done():
            if not self.stopped:
                return self._task
            self._task.cancel()
        self.stopped = False
        self._task = asyncio.create_task(self._run())
        return self._task

    async def _run(self) -> None:
        try:
            while not self.stopped:
                await self.beat()
                if self.stopped:
                    break
                await asyncio.sleep(self.current_interval_sec)
        except asyncio.CancelledError:
            pass

    def stop(self) -> None:
        self.stopped = True
        if self._task is not None and not self._task.done():
            self._task.cancel()
        self.current_step = 0
        self.current_beat_in_step = 0

    def pause(self) -> None:
        self.stopped = True
        if self._task is not None and not self._task.done():
            self._task.cancel()

    @staticmethod
    def snap_measures_to_power_of_2(input: int) -> int:
        if input <= 1:
            return 1
        return 2 ** (input - 1).bit_length()

    def __setattr__(self, name: str, value: any) -> None:
        if name == "measure" and isinstance(value, int):
            value = self.snap_measures_to_power_of_2(value)
        super().__setattr__(name, value)
        if hasattr(self, "_listeners") and name != "_listeners":
            for listener in list(self._listeners):
                listener(name, value)
