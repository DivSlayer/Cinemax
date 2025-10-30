import json
import re
from PIL import Image
import requests
from bs4 import BeautifulSoup
from imdb import Cinemagoer, os

from django.utils.text import slugify
from Person.models import Person
from Person.values import get_person_root
from Utility.bsoup_parser import BsoupParser


class ActorHandler:

    def __init__(self,
                 person_id,
                 name,
                 folder='media/persons',
                 check_exist=True):
        self.person_id = person_id
        self.name = name
        self.folder = folder
        self.check_exist = check_exist
        self.img = None
        self.bio = None
        self.height = None
        self.birth_date = None
        self.parser = None
        self.person = None

    def get_safe_words(self, string):
        list_words = []
        for word in string.strip().split(" "):
            check = re.match(r"[0-9A-Za-z]", word)
            if check is not None:
                list_words.append(check.string.lower())
        input_string = ' '.join(list_words)
        input_string = input_string.encode("latin", "ignore")
        input_string = input_string.decode("utf-8", "ignore")
        input_string = input_string.replace("'", '')
        input_string = input_string.replace(":", "").lower()
        inpurt_string = " ".join(slugify(input_string).split("-"))
        return input_string

    def initialize(self):
        ia = Cinemagoer()
        ia_actor = ia.get_person(self.person_id)
        with open('media/xmls/person-xml.xml', 'w', encoding='utf-8') as f:
            f.write(ia_actor.asXML())
        with open('media/xmls/person-xml.xml', 'r', encoding='utf-8') as f:
            data = f.read()
        bs_data = BeautifulSoup(data, 'xml')
        self.parser = BsoupParser(bs_data)

    def get_db_person(self):
        instance = Person.objects.get(imdb_id=self.person_id)
        return instance

    def make_compress(self, person):
        if self.img is not None:
            image = Image.open(f"media/{self.img}")
            img_path = f"{get_person_root(person, use_media=True)}image.jpg"
            image.save(img_path,
                       "JPEG",
                       optimize=True,
                       quality=50)

    def start(self):
        try:
            check_actors = len(
                Person.objects.filter(imdb_id=self.person_id))
            if check_actors > 0 and self.check_exist is True:
                return self.get_db_person()
            else:
                self.initialize()
                self.set_data()
                actor_instance = self.save_person_db()
                return actor_instance
        except Exception as e:
            print(f"\n[Actor HANDLER ERROR] {e}\n")
            raise e
            return None

    def set_data(self):
        image_path = f'{self.folder}/{self.get_safe_words(self.name)}-{self.person_id}/'
        if self.parser.find_item('full-size-headshot').text() is not None:
            self.img = self.parser.find_item('full-size-headshot').text()
            self.img = self.get_headshot(self.img, image_path)
        self.height, self.birth_date, self.age = self.get_celeb_info()
        self.name = str(self.name).lower()

    def get_celeb_info(self):
        api_url = 'https://api.api-ninjas.com/v1/celebrity?name={}'.format(self.name)
        response = requests.get(api_url, headers={'X-Api-Key': 'IQ3r/P2aWcdELF+xsd9hYw==kkYZ0YAj1gSorKqD'})
        if response.status_code == requests.codes.ok:
            jsonified = json.loads(response.text)
            jsonified = jsonified[0] if len(jsonified) > 0 else None
            if jsonified is not None:
                height = jsonified["height"] if "height" in dict(jsonified).keys() else None
                age = jsonified["age"] if "age" in dict(jsonified).keys() else None
                birthday = jsonified["birthday"] if "birthday" in dict(jsonified).keys() else None
                return height, birthday, age
            return None, None, None
        else:
            return None, None, None

    def get_headshot(self, url, path, file_name='image.jpg'):
        if url is not None:
            detail_req = requests.get(url)
            os.makedirs(os.path.join(os.getcwd(), path), exist_ok=True)
            detail_path = path + file_name
            open(detail_path, "wb").write(detail_req.content)
            detail_path = "/".join(detail_path.split('/')[1:])
            return detail_path
        return None

    def save_person_db(self):
        persons = Person.objects.filter(imdb_id=self.person_id)
        if len(persons) == 0:
            person_instance = Person.objects.create()
            person_instance.imdb_id = self.person_id
            person_instance.name = self.name.lower()
            person_instance.img.name = self.img
            person_instance.bio = self.bio
            person_instance.height = self.height
            person_instance.birth_date = self.birth_date
            person_instance.save()
            self.preson = person_instance
            self.make_compress(person_instance)
        else:
            person_instance = persons[0]
        return person_instance
