from googletrans import Translator

from Category.models import Category


class CategoryHandler:
    def __init__(self, en_title):
        self.en_title = en_title

    def start(self):
        check = Category.objects.filter(en_title=self.en_title)
        if len(check) > 0:
            return check.first()
        else:
            new_instance = Category.objects.create(en_title=self.en_title)
            new_instance.fa_title = Translator().translate(str(self.en_title), dest='fa').text
            new_instance.save()
            return new_instance
