from bs4 import BeautifulSoup


class BsoupParser:

    def __init__(self, bsoup):
        self.bsoup = bsoup
        self.item = bsoup
        self.items = []

    def find_item(self, key):
        item = self.bsoup.find(key)
        self.item = item
        return self

    def text(self, attr=None):
        if self.item is not None:
            if attr is not None:
                if attr in self.item.attrs:
                    return self.item[attr]
                return None
            return self.item.text.strip()
        return None

    def for_list(self, key=None, attr=None, raw=False):
        arr = []
        for item in self.items:
            if key is not None:
                if attr is not None:
                    found = item.find(key)[attr]
                    if found is not None:
                        arr.append(found.strip())
                else:
                    found = item.find(key)
                    if found is not None:
                        arr.append(found.text.strip())
            else:
                if attr is not None:
                    found = item[attr]
                    if found is not None:
                        arr.append(found.strip())
                else:
                    if raw:
                        arr.append(item)
                    else:
                        arr.append(item.text.strip())
        return arr

    def find_all(self, key):
        if self.item is not None:
            items = self.item.find_all(key)
            self.items = items
        return self
