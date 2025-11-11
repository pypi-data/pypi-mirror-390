# Anny
# Copyright (C) 2025 NAVER Corp.
# Apache License, Version 2.0
import pathlib
import os

ANNY_ROOT_DIR = pathlib.Path(__file__).resolve().parent

# Define the default cache directory as a fixed, absolute path (user-overridable)
DEFAULT_CACHE_PATH = pathlib.Path.home() / ".cache" / "anny"
ANNY_CACHE_DIR = pathlib.Path(os.getenv("ANNY_CACHE_DIR", str(DEFAULT_CACHE_PATH)))
