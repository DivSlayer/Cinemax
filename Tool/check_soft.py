from Tool.audio_handler import AudioHandler
from Tool.get_soft_subtitle import SoftSubtitle
from Utility.no_serializer import get_object


def check_soft_sub(file_name, uuid):
    obj = get_object(uuid, use_imdb=False, use_slug=False)
    if not obj.subbed:
        extras = file_name.split(".")
        for word in extras:
            if word.lower() == "softsub" or word.lower() == "soft":
                print('It Has Subtitle')
                ins = SoftSubtitle([uuid])
                done_subs = ins.action()
                print(f"donesubs:{len(done_subs)}")
                if type(done_subs) == list and len(done_subs) > 0:
                    ins = SoftSubtitle([uuid])
                    ins.remove_sub()
                    ins.add_soft_to_video([sub.srt.path for sub in done_subs])
                obj = get_object(uuid, use_imdb=False)
                obj.subbed = True
                obj.save()
            if word.lower() == "hardsub" or word.lower() == "hard":
                obj = get_object(uuid, use_imdb=False)
                print("hard subebd")
                obj.subbed = True
                obj.save()
        extras = [word.lower() for word in extras]
        if 'softsub' not in extras and 'soft' not in extras:
            ins = SoftSubtitle([uuid])
            ins.remove_sub()
    for word in file_name.split("."):
        if word.lower() == "dubbed":
            obj = get_object(uuid, use_imdb=False)
            AudioHandler(obj).action()
            obj.dubbed = True
            obj.save()
