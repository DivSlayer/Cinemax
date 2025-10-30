from Movie.models import Video


class SocketMessage:
    def __init__(self, video:Video, new_data=None):
        self.video = video
        self.new_data = new_data

    def serialize(self):
        data = {
            "uuid": self.video.uuid,
            "current_step": self.video.json_data['current_step'] if "current_step" in dict(self.video.json_data).keys() else "",
            "steps": self.video.json_data['steps'] if "steps" in dict(self.video.json_data).keys() else [],
            "total_progress": self.video.json_data['total_progress'] if "total_progress" in dict(self.video.json_data).keys() else 0,
            "step_progress": self.video.json_data['step_progress'] if "step_progress" in dict(self.video.json_data).keys() else 0,
            "remained_time": self.video.json_data['remained_time'] if "remained_time" in dict(self.video.json_data).keys() else None,
            'error': self.video.json_data['error'] if "error" in dict(self.video.json_data).keys() else None
        }
        if self.new_data:
            data.update(self.new_data)
        return data
