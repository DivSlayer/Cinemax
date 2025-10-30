class Env:
    def __init__(self) -> None:
        self.SERVER = "http://192.168.0.232"
        self.API_KEY = "a776ea545eb6eb3d6f014ed9946b8cc8"
        self.import_sites = ['digimoviez', 'donyayeserial', 'zarfilm', 'zfilm', 'filmkio', '30nama', 'avamovie',
                             'دیجی موویز', 'زرفیلم',
                             'زر فیلم', 'زد فیلم', 'زدفیلم', 'آوا مووي', 'آوامووي', 'cinemax', 'سینمکس','دنیای سریال','دنیایسریال']

    def get_server(self):
        with open("current_server.txt", "r") as f:
            data = f.read()
            if data != "":
                self.SERVER = f"http://{data.replace(' ', '').strip()}"
            else:
                self.SERVER = "http://192.168.0.232"
        return self.SERVER
