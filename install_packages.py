import os

packages = [
    "pillow",
    "opencv-python",
    "dj-static",
    "static-ranges",
    "qrcode",
    "beautifulsoup4",
    "pandas",
    "requests",
    "cinemagoer",
    "scipy",
    "djangorestframework",
    "webvtt-py",
    "googletrans==3.1.0a0",
    "pyyaml ua-parser user-agents",
    "django-user-agents",
    "mysqlclient",
    "djangorestframework-simplejwt",
    "django-cors-headers",
    "mysqlclient",
    "setuptools"
]

for package in packages:
    command = (
        f"cd G:/Movies/Cinemax/venv/scripts && activate && pip install {package}"
    )
    os.system(command)
