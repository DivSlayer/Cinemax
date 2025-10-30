import qrcode
import qrcode.image.svg


class GetQRCode:
    def __init__(self, data):
        self.data = data

    def start(self):
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5,
            image_factory=qrcode.image.svg.SvgPathImage,
        )
        qr.add_data(str(self.data))
        qr.make(fit=True)
        img = qr.make_image()
        strint = img.to_string(encoding="unicode")
        return strint
