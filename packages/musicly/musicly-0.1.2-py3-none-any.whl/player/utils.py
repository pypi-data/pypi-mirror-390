#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: utils.py
Author: Maria Kevin
Created: 2025-11-09
Description: Utility functions for downloading audio using YT-DLP.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"


import subprocess
import os

DOWNLOAD_DIR = "downloads"


def download_audio(name: str):
    """Download audio by name using YT-DLP."""

    # Create download directory if it doesn't exist
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # yt-dlp ytsearch1:"Artist - Track Name" -x --audio-format mp3 -o "%(title)s.%(ext)s"
    path = f"{name}.mp3"
    full_path = os.path.join(DOWNLOAD_DIR, path)
    cmd = [
        "yt-dlp",
        f"ytsearch1:{name}",
        "-x",
        "--audio-format",
        "mp3",
        "-o",
        full_path,
    ]

    result = subprocess.run(cmd)

    if result.returncode != 0:
        return None

    return full_path
