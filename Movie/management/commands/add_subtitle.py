import os
import shutil

from Movie.management.commands.step_function import StepFunction
from Movie.models import Video, Subtitle
from Movie.values import get_movie_root
from Tool.add_intro import get_video_duration
from Tool.get_soft_subtitle import SoftSubtitle


class AddSubtitle:
    def __init__(self, video: Video):
        self.video = video
        self.steps = []
        self.temp_video = None
        self.subs = Subtitle.objects.filter(video=self.video)
        self.original_intro = os.path.join(os.getcwd(), 'media', 'env', 'intro.mp4')
        self.soft_ins = SoftSubtitle([video.uuid])
        self.calculate_steps()

    def calculate_steps(self):
        if self.video.subbed and len(self.subs) == 0:
            self.steps.append(StepFunction(name="Extracting Subtitles", function=self.extract_subtitle,
                                           post_functions=self.soft_ins.post_extracting))
        if self.video.has_intro:
            self.steps.append(StepFunction(name="Adjusting Subtitle", function=self.adjust_subtitle_timing))
        if self.video.subbed:
            self.steps.append(StepFunction(name="Removing Subtitles", function=self.remove_video_subtitles,
                                       post_functions=self.soft_ins.post_remove_processing))
        self.steps.append(StepFunction(name="Adding Subtitles", function=self.add_subtitle,
                                       post_functions=self.soft_ins.post_add_processing))

    def adjust_subtitle_timing(self):
        subs = Subtitle.objects.filter(video=self.video)
        intro_duration = get_video_duration(self.original_intro)
        for sub in subs:
            SoftSubtitle([]).adjust_srt_timing(input_file=sub.srt.path, shift_seconds=intro_duration,
                                               vtt_path=sub.vtt.path)
        return [None], [None]

    def extract_subtitle(self):
        """
        This function will extract the subtitles from the video
        """
        processes, contexts = self.soft_ins.action()
        return processes, contexts

    def remove_video_subtitles(self):
        """
        This function will remove all the subtitle from video
        """
        processes, contexts = self.soft_ins.remove_sub()
        return processes, contexts

    def add_subtitle(self):
        """
        This function will add all the subtitles to the video
        """
        ext = self.video.file.name.split('.')[-1]
        self.temp_video = os.path.join(os.getcwd(), get_movie_root(self.video.movie, use_media=True,
                                                                   filepath=f"video-no-subs.{ext}"))
        input_path = self.temp_video if os.path.isfile(self.temp_video) else self.video.file.path
        output_video = self.video.file.path if os.path.isfile(self.temp_video) else self.temp_video
        subs = Subtitle.objects.filter(video=self.video)
        processes, contexts = self.soft_ins.add_soft_to_video(subs_path=[sub.srt.path for sub in subs],
                                                              input_path=input_path,
                                                              output_path=output_video)
        return processes, contexts


    def cleanup(self):
        """
        Cleaning up after the job is done
        """
        has_remove_sub = any(step.name == "Removing Subtitles" for step in self.steps)
        if self.temp_video and os.path.isfile(self.temp_video):
            if has_remove_sub:
                os.remove(self.temp_video)
            else:
                shutil.move(self.temp_video,self.video.file.path)