import re
import time

from django.core.management import BaseCommand
from django.utils import timezone

from Movie.management.commands.add_subtitle import AddSubtitle
from Movie.management.commands.process_base import ProcessBase
from Movie.management.commands.socket_message import SocketMessage
from Movie.management.commands.step_function import StepFunction
from Movie.models import Video
from Tool.add_intro import get_video_duration


class Command(ProcessBase):
    help = 'Process queued video subtitle in the background'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.process_class = AddSubtitle

    def handle(self, *args, **options):
        """ This function will listen to changes of the video for each 5 seconds """
        super().handle(action='subtitle')

    def finish_up(self, *args, **options):
        self.video.subbed = True

        super().finish_up()