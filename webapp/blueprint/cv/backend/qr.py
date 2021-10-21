#  Copyright 2021 Ismael Lugo <ismaelrlg.dev@gmail.com>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
from PIL import Image
from qrcode import constants
from qrcode import QRCode


class CustomQRCode:
    DEFAULT_EXT = 'png'

    def __init__(self):
        self.logo = None
        self.width = 100

    def add_logo(self, logo_path: str):
        self.logo = Image.open(logo_path)

        # adjust image size
        w = self.width / float(self.logo.size[0])
        h = int(float(self.logo.size[1]) * float(w))
        self.logo = self.logo.resize((self.width, h), Image.ANTIALIAS)

    def get_qr_code(self, url):
        qr_code = QRCode(error_correction=constants.ERROR_CORRECT_H)
        qr_code.add_data(url)
        qr_code.make()

        qr_logo = qr_code.make_image(fill_color='Black', back_color='white')
        qr_logo = qr_logo.convert('RGB')

        if self.logo is not None:
            pos = (
                (qr_logo.size[0] - self.logo.size[0]) // 2,
                (qr_logo.size[1] - self.logo.size[1]) // 2,
            )
            qr_logo.paste(self.logo, pos)
        return qr_logo


qr = CustomQRCode()
