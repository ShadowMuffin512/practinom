from dataclasses import field

import flet as ft

import consts
from audio_player import AudioPlayer
from metronome import Metronome

BG_COLOR = "#8BBF9F"
MAIN_COLOR = "#2D232E"
ACCENT_COLOR = "#474448"
CARD_BG = "#FFFFFF"
INPUT_BG = "#F4F8F5"
INPUT_BORDER = "#D6E5DC"
BORDER_RADIUS = 12


@ft.control
class PractinomInput(ft.TextField):
    bgcolor: str = INPUT_BG
    color: str = MAIN_COLOR
    border_color: str = INPUT_BORDER
    focused_border_color: str = MAIN_COLOR
    border_radius: int = BORDER_RADIUS
    cursor_color: str = MAIN_COLOR
    text_size: int = 15
    dense: bool = True
    expand: int = 1
    text_style: ft.TextStyle = field(
        default_factory=lambda: ft.TextStyle(
            color=MAIN_COLOR, weight=ft.FontWeight.W_600
        )
    )
    label_style: ft.TextStyle = field(
        default_factory=lambda: ft.TextStyle(
            color=ACCENT_COLOR, size=12, weight=ft.FontWeight.W_500
        )
    )


@ft.control
class PractinomNumberInput(PractinomInput):
    input_filter: ft.InputFilter = field(default_factory=ft.NumbersOnlyInputFilter)
    keyboard_type: ft.KeyboardType = ft.KeyboardType.NUMBER
    expand: int = 1


@ft.control
class PractinomButton(ft.Button):
    bgcolor: str = MAIN_COLOR
    color: str = "#FFFFFF"
    height: int = 46
    expand: int = 1
    style: ft.ButtonStyle = field(
        default_factory=lambda: ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            elevation=1,
        )
    )


def setup_buttons(page: ft.Page, metronome: Metronome):
    input_fields: dict[str, PractinomNumberInput] = {}

    reps_left = ft.Text(
        value=f"x{metronome.measures_left!s}",
        size=11,
        weight=ft.FontWeight.W_700,
        color="#FFFFFF",
    )

    starting_tempo_display = ft.Text(
        value=str(metronome.starting_tempo),
        size=32,
        weight=ft.FontWeight.BOLD,
        color="#FFFFFF",
    )

    arrow_symbol_left = ft.Text(
        value="→",
        size=32,
        weight=ft.FontWeight.BOLD,
        color="#FFFFFF",
    )

    arrow_symbol_right = ft.Text(
        value="→",
        size=32,
        weight=ft.FontWeight.BOLD,
        color="#FFFFFF",
    )

    current_tempo_display = ft.Text(
        value=str(metronome.current_tempo),
        size=48,
        weight=ft.FontWeight.BOLD,
        color="#FFFFFF",
    )

    ending_tempo_display = ft.Text(
        value=str(metronome.ending_tempo),
        size=32,
        weight=ft.FontWeight.BOLD,
        color="#FFFFFF",
    )

    progression_summary = ft.Text(
        value=f"{'+' if metronome.step_size > 0 else ''}{metronome.step_size} BPM/step",
        size=11,
        color="#A7C2B2",
    )

    beat_dots_row = ft.Row(
        controls=[],
        spacing=8,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        height=16,
    )

    def render_beat_dots(active_idx: int = -1):
        dots = []
        count = min(max(metronome.beats_per_measure, 1), 16)

        for i in range(count):
            is_active = i == active_idx

            dots.append(
                ft.Container(
                    width=12,
                    height=12,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Container(
                        width=12 if is_active else 8,
                        height=12 if is_active else 8,
                        border_radius=6,
                        bgcolor=(BG_COLOR if i == 0 else "#FFFFFF")
                        if is_active
                        else ACCENT_COLOR,
                        animate=ft.Animation(100, ft.AnimationCurve.EASE_OUT),
                    ),
                )
            )

        beat_dots_row.controls = dots

    render_beat_dots()

    def on_input_change(field_name: str, default: int):
        def handler(e: ft.ControlEvent):
            try:
                val = int(e.control.value) if e.control.value else default
            except ValueError:
                val = default
            setattr(metronome, field_name, val)
            sync_hero_display()

        return handler

    def sync_hero_display():
        current_tempo_display.value = str(metronome.current_tempo)
        reps_left.value = f"x{metronome.measures_left!s}"
        progression_summary.value = (
            f"{'+' if metronome.step_size > 0 else ''}{metronome.step_size} BPM/step"
        )
        render_beat_dots()
        hero_card.update()

    def on_metronome_change(field_name: str, value: any):
        control = input_fields.get(field_name)
        if control and control.value != str(value):
            control.value = str(value)
            control.update()

        if field_name == "current_beat_in_step":
            current_tempo_display.value = str(metronome.current_tempo)
            reps_left.value = f"x{metronome.measures_left!s}"
            if metronome.beats_per_measure > 0 and metronome.current_beat_in_step > 0:
                active_beat = (
                    metronome.current_beat_in_step - 1
                ) % metronome.beats_per_measure
                render_beat_dots(active_beat)
            else:
                render_beat_dots(-1)
            hero_card.update()

        elif field_name in (
            "current_step",
            "starting_tempo",
            "ending_tempo",
            "steps",
            "measures_per_step",
            "beats_per_measure",
        ):
            starting_tempo_display.value = str(metronome.starting_tempo)
            ending_tempo_display.value = str(metronome.ending_tempo)
            current_tempo_display.value = str(metronome.current_tempo)
            reps_left.value = f"x{metronome.measures_left!s}"
            progression_summary.value = f"{'+' if metronome.step_size > 0 else ''}{metronome.step_size} BPM/step"
            render_beat_dots()
            hero_card.update()

        elif field_name == "stopped":
            if value:
                render_beat_dots(-1)
                hero_card.update()

    metronome.add_listener(on_metronome_change)

    beats_input = PractinomNumberInput(
        label="Ticks / Rep",
        value=str(metronome.beats_per_measure),
        on_blur=on_input_change("beats_per_measure", metronome.beats_per_measure),
    )
    starting_tempo_input = PractinomNumberInput(
        label="Start Tempo",
        value=str(metronome.starting_tempo),
        suffix="BPM",
        on_blur=on_input_change("starting_tempo", metronome.starting_tempo),
    )
    ending_tempo_input = PractinomNumberInput(
        label="Target Tempo",
        value=str(metronome.ending_tempo),
        suffix="BPM",
        on_blur=on_input_change("ending_tempo", metronome.ending_tempo),
    )
    steps_input = PractinomNumberInput(
        label="Total Steps",
        value=str(metronome.steps),
        on_blur=on_input_change("steps", metronome.steps),
    )
    measures_per_step_input = PractinomNumberInput(
        label="Reps / Step",
        value=str(metronome.measures_per_step),
        on_blur=on_input_change("measures_per_step", metronome.measures_per_step),
    )

    input_fields.update(
        {
            "beats_per_measure": beats_input,
            "starting_tempo": starting_tempo_input,
            "ending_tempo": ending_tempo_input,
            "steps": steps_input,
            "measures_per_step": measures_per_step_input,
        }
    )

    header_section = ft.Row(
        controls=[
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.SPEED_ROUNDED,
                            color=BG_COLOR,
                            size=24,
                        ),
                        bgcolor=MAIN_COLOR,
                        border_radius=12,
                        padding=8,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                value="PRACTINOM",
                                size=20,
                                weight=ft.FontWeight.W_800,
                                color=MAIN_COLOR,
                            ),
                            ft.Text(
                                value="Practice metronome, made by Lior Dahan",
                                size=11,
                                color=ACCENT_COLOR,
                                weight=ft.FontWeight.W_500,
                            ),
                        ],
                        spacing=1,
                    ),
                ],
                spacing=12,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    hero_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[reps_left],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                ),
                ft.Row(
                    controls=[
                        ft.Row(
                            controls=[starting_tempo_display, arrow_symbol_left],
                            expand=1,
                            spacing=8,
                            alignment=ft.MainAxisAlignment.END,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        current_tempo_display,
                        ft.Row(
                            controls=[arrow_symbol_right, ending_tempo_display],
                            expand=1,
                            spacing=8,
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[
                        beat_dots_row,
                        progression_summary,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    wrap=True,
                ),
            ],
            spacing=8,
        ),
        bgcolor=MAIN_COLOR,
        border_radius=18,
        padding=ft.Padding.symmetric(horizontal=20, vertical=18),
    )

    tempo_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[beats_input],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[starting_tempo_input, ending_tempo_input],
                    spacing=12,
                ),
                ft.Row(
                    controls=[steps_input, measures_per_step_input],
                    spacing=12,
                ),
            ],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
        padding=16,
    )

    def on_play_click(e):
        metronome.play()

    def on_pause_click(e):
        metronome.pause()

    def on_stop_click(e):
        metronome.stop()
        sync_hero_display()

    play_button = PractinomButton(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, color=BG_COLOR, size=22),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=6,
        ),
        bgcolor=MAIN_COLOR,
        expand=2,
        on_click=on_play_click,
    )

    pause_button = PractinomButton(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.PAUSE_ROUNDED, color="#FFFFFF", size=20),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=4,
        ),
        bgcolor=ACCENT_COLOR,
        on_click=on_pause_click,
    )

    stop_button = PractinomButton(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.STOP_ROUNDED, color="#FFFFFF", size=20),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=4,
        ),
        bgcolor=ACCENT_COLOR,
        on_click=on_stop_click,
    )

    controls_bar = ft.Row(
        controls=[play_button, pause_button, stop_button],
        spacing=10,
    )

    main_card = ft.Container(
        content=ft.Column(
            controls=[
                header_section,
                hero_card,
                tempo_card,
                controls_bar,
            ],
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
        width=440,
        bgcolor=CARD_BG,
        border_radius=22,
        padding=20,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=18,
            color="#18000000",
            offset=ft.Offset(0, 6),
        ),
    )
    page.add(main_card)


def main(page: ft.Page):
    audio_player = AudioPlayer(1)
    metronome = Metronome(60, 140, 10, 4, 4, audio_player)
    page.services.extend(audio_player.get_services())
    page.update()

    page.title = "Practinom • Practice Metronome"
    page.bgcolor = BG_COLOR
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    setup_buttons(page, metronome)
    page.update()


if __name__ == "__main__":
    ft.run(main, assets_dir=str(consts.ASSETS_DIR))
