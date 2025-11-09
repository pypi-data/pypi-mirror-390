#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: main.py
Author: Maria Kevin
Created: 2025-11-09
Description: A terminal-based music player that allows users to search and play songs directly from the command line.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"

from typer import Typer, Argument
from just_playback import Playback
import time

from .utils import download_audio

app = Typer()


@app.command()
def play(
    name: str = Argument(
        ..., help="The name of the song to play, example: 'All the stars'"
    ),
    loop: bool = False,
):
    """Play a song by name."""

    print(f"Downloading and playing: {name}")
    audio_path = download_audio(name)

    if not audio_path:
        print("Failed to download the audio.")
        return

    print(f"Playing audio from: {audio_path}")

    playback = Playback()
    playback.load_file(audio_path)

    while True:
        playback.play()

        while playback.active:
            time.sleep(1)

        if not loop:
            break


if __name__ == "__main__":
    app()
