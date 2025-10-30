import re
import time

from django.core.management import BaseCommand
from django.utils import timezone

from Movie.management.commands.process_base import ProcessBase
from Movie.management.commands.socket_message import SocketMessage
from Movie.management.commands.step_function import StepFunction
from Movie.models import Video
from Tool.add_intro import AddIntro, get_video_duration


def time_to_seconds(time_str):
    hours, minutes, seconds = map(float, time_str.split(':'))
    return hours * 3600 + minutes * 60 + seconds


def parse_time_from_process(line):
    time_pattern = re.compile(r'time=(\d+:\d+:\d+\.\d+)')
    if match := time_pattern.search(line):
        return match
    return False


class Command(ProcessBase):
    help = 'Process queued video intro in the background'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.process_class = AddIntro

    def handle(self, *args, **options):
        super().handle(action="intro")

    def calculate_progress(self, current_step: StepFunction, match, completed_processes: int,
                           total_processes: int, process_class, duration=None):
        concatenate_step = next((item for item in process_class.steps if item.name.lower() == "Concatenating videos"),
                                None)
        if concatenate_step:
            index_of = process_class.steps.index(concatenate_step)
            current_index = process_class.steps.index(current_step)
            if current_index >= index_of:
                duration = get_video_duration(self.video.file.path) + 10.4
            else:
                duration = get_video_duration(self.video.file.path)
        else:
            duration = get_video_duration(self.video.file.path)
        super().calculate_progress(current_step, match, completed_processes, total_processes, duration=duration,
                                   process_class=process_class)

    def finish(self, *args, **options):
        self.video.has_intro = True
        super().finish_up()
