import asyncio
import inspect
import re
import time

from django.core.management import BaseCommand
from django.utils import timezone

from Movie.management.commands.socket_message import SocketMessage
from Movie.management.commands.step_function import StepFunction
from Movie.models import Video
from Tool.add_intro import get_video_duration


def time_to_seconds(time_str):
    hours, minutes, seconds = map(float, time_str.split(':'))
    return hours * 3600 + minutes * 60 + seconds


def parse_time_from_process(line):
    time_pattern = re.compile(r'time=(\d+:\d+:\d+\.\d+)')
    if match := time_pattern.search(line):
        return match
    return False


class ProcessBase(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.video = None
        self.steps = None
        self.completed_steps = 0
        self.process_class = None

    def handle(self, action: str, *args, **options):
        self.stdout.write("Starting video processing worker...")
        while True:
            video = Video.objects.filter(status='queued', action=action).first()
            if video:
                self.process_video(video)
            else:
                time.sleep(5)

    def process_video(self, video):
        self.video = video
        process_class = self.process_class(video)
        try:
            self.handle_initiation(process_class)
            self.finish_up()
        except Exception as e:
            self.handle_error(e)

    def finish_up(self):
        self.video.last_updated = timezone.now()
        self.video.status = "completed"
        self.video.save()
        self.stdout.write(f"Finished self.video {self.video.id}")

    def handle_error(self, e):
        raise e
        print(f"[ERROR] {e}")
        self.video.status = 'failed'
        self.video.error_message = str(e)
        self.video.json_data = SocketMessage(self.video, new_data={"error": str(e), 'status': 'failed'}).serialize()
        self.video.save()
        self.stdout.write(self.style.ERROR(f"self.video {self.video.id} failed: {str(e)}"))

    def handle_initiation(self, process_class):
        self.video.status = 'processing'
        self.video.error_message = None
        self.video.last_updated = timezone.now()
        self.video.save()
        self.stdout.write(f"Processing self.video {self.video.movie.title} {self.video.resolution}")
        self.video.json_data = SocketMessage(self.video, new_data={
            "steps": [item.name for item in process_class.steps]}).serialize()
        self.video.save()
        for step in process_class.steps:
            self.run_step(step, process_class)
        process_class.cleanup()

    def run_step(self, current_step: StepFunction, process_class):
        self.video.json_data = SocketMessage(self.video, {"current_step": current_step.name}).serialize()
        self.video.save()
        start_time = time.time()
        print(current_step.name)
        # Execute step function and get processes + context
        processes, contexts = current_step.run_func()
        # This is the loop for steps
        completed_processes = 0
        if isinstance(processes, list) and len(processes) > 0:
            while processes:
                for i, (process, context) in enumerate(zip(processes[:], contexts[:])):
                    if process is None or not hasattr(process, 'stderr'):
                        processes.remove(process)
                        contexts.remove(context)
                        total_progress = min(
                            self.calculate_total_progress(process_class,100), 100)

                        self.video.json_data = SocketMessage(self.video, {"step_progress": 100,
                                                                          "total_progress": total_progress}).serialize()
                        self.video.save()

                        self.completed_steps += 1
                        continue
                    line = process.stderr.readline()
                    if line:
                        line = line.strip()
                        match = parse_time_from_process(line)
                        if match:
                            self.calculate_progress(current_step=current_step,
                                                    match=match, total_processes=len(processes),
                                                    completed_processes=completed_processes,
                                                    process_class=process_class)
                    # Check if process completed
                    if process.poll() is not None:
                        print("done process")
                        completed_processes += 1
                        # Handle post-processing
                        if current_step.post_functions is not None:
                            current_step.post_functions(context)

                        processes.remove(process)
                        contexts.remove(context)
                        # Update progress
                        total_progress = self.calculate_total_progress(process_class,100)
                        self.completed_steps += 1
                        self.video.json_data = SocketMessage(self.video, {
                            "total_progress": total_progress,
                            "step_progress": 100
                        }).serialize()
                        self.video.save()
        elif isinstance(processes, list) and len(processes) == 0:
            print(f"{current_step.name} has no processes")
            total = self.calculate_total_progress(process_class, 100)
            self.completed_steps += 1
            self.video.json_data = SocketMessage(self.video, {
                "total_progress": total,
                "step_progress": 100
            }).serialize()
        end_time = time.time()
        print(f"{current_step.name} took {end_time - start_time} seconds")

    def calculate_total_progress(self, process_class, step_progress: int):
        weight_of_steps = 100 / len(process_class.steps)
        base_of_progress = self.completed_steps * weight_of_steps
        total_progress = base_of_progress + (step_progress / len(process_class.steps))
        return total_progress

    def calculate_progress(self, current_step: StepFunction, match, completed_processes: int,
                           total_processes: int, process_class, duration=None):
        duration = duration if duration is not None else get_video_duration(self.video.file.path)
        current_time = time_to_seconds(match.group(1))
        time_progress = min((current_time / duration) * 100, 100) if duration > 0 else 0
        process_weight = 100 / total_processes
        base_progress = completed_processes * process_weight
        step_progress = base_progress + time_progress / total_processes
        total_progress = min(self.calculate_total_progress(step_progress=step_progress, process_class=process_class),
                             100)
        self.video.json_data = SocketMessage(self.video, {
            "total_progress": total_progress,
            "step_progress": step_progress,
            "remained_time": duration - current_time
        }).serialize()
        self.video.last_updated = timezone.now()
        self.video.save()
