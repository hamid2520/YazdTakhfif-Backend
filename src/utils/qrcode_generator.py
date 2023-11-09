import qrcode
from io import BytesIO


def text_to_qrcode(text):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    byte_stream = BytesIO()
    img.save(byte_stream)
    byte_stream.seek(0)
    return byte_stream.read()
