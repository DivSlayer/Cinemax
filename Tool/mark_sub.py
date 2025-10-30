
import json
import re
import environ
from django.conf import settings


class MarkSub:
    def __init__(self, file):
        self.file = file
        self.lines = []
        self.sites = settings.env.list("IMPORT_SITES", default=[])

        self.new_content = None
        self.read_content()

    def website_check(self, line):
        url_regex = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](
            ?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af
            |ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch
            |ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf
            |gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km
            |kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz
            |na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg
            |sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy
            |uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([
            ^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[
            .\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel
            |travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw
            |by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk
            |fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je
            |jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr
            |ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs
            |ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt
            |tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
        return re.match(url_regex, str(line).strip()) is not None

    def email_check(self, line):
        email_regex = r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
        return re.match(email_regex, str(line).strip()) is not None

    def channel_check(self, line): 
        return line.find('@') != -1

    def site_replacing(self, string: str):
        has_it = False
        for site in self.sites:
            if string.lower().find(site) != -1:
                has_it = True
        return has_it

    def add_own_mark(self, content):
        mark = ''
        with open('Cinemax/mark.txt', 'r', encoding='utf8') as f:
            mark = f.read()
        mark += '\n'
        for line in content:
            try:
                value = line.replace('\n', '').strip()
                integer = int(value)
                integer = integer + 2
                new_def = f"{integer}\n"
            except Exception as e:
                new_def = line
            mark += str(new_def)
        return mark

    def get_safe_words(self, string):
        list_words = []
        for word in string.strip().split(" "):
            check = re.match(r"[0-9A-Za-z]", word)
            if check is not None:
                list_words.append(check.string.lower())
            else:
                list_words.append(re.sub(r'[^a-zA-Z0-9\s]', '', word))
        input_string = ' '.join(list_words)
        input_string = input_string.encode("latin", "ignore")
        input_string = input_string.decode("utf-8", "ignore")
        input_string = input_string.replace("'", '')
        input_string = input_string.replace(":", "").lower()
        return input_string

    def read_content(self):
        with open(self.file, 'r', encoding='utf-8') as f:
            self.lines = f.readlines()
        pured_lines = [line.strip() for line in self.lines]
        branches = []
        current_branch = ''
        for line in pured_lines:
            line = line.replace('\ufeff','')
            has_site_name = self.site_replacing(line)
            pure_content = self.get_safe_words(line)
            have_website = self.website_check(pure_content)
            have_email = self.email_check(pure_content)
            have_channel = self.channel_check(pure_content)
            if has_site_name:
                current_branch = ''
            elif have_channel:
                current_branch = ''
            elif have_email:
                current_branch = ''
            elif have_website:
                current_branch = ''
            else:
                if line != '':
                    try:
                        integered = int(line)
                        if current_branch != '':
                            branches.append(current_branch)
                        current_branch = f'\n{len(branches) + 3}\n'
                    except Exception as e:
                        current_branch += f'{line}\n'
        self.new_content = self.add_own_mark(branches)

    def save_file(self, new_name):
        with open(new_name, 'w', encoding='utf8') as f:
            f.write(self.new_content)

    def get_content(self):
        return self.new_content
