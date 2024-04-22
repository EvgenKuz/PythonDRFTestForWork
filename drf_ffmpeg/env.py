# Build paths inside the project like this: BASE_DIR / 'subdir'.
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# environment variable getter
env = environ.Env()
env.read_env(Path.joinpath(BASE_DIR, ".env"))
