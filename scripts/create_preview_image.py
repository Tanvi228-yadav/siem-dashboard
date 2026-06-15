import zlib
import binascii
from pathlib import Path

path = Path(__file__).resolve().parent.parent / 'assets' / 'dashboard-preview.png'
width, height = 200, 80
pixels = []
for y in range(height):
    for x in range(width):
        if 10 < x < 190 and 20 < y < 60:
            pixels.extend((180, 220, 240, 255))
        else:
            pixels.extend((40, 40, 90, 255))
raw = b''.join(b'\x00' + bytes(pixels[y * width * 4:(y + 1) * width * 4]) for y in range(height))
with open(path, 'wb') as f:
    f.write(b'\x89PNG\r\n\x1a\n')

    def chunk(chunk_type, data):
        f.write(len(data).to_bytes(4, 'big'))
        f.write(chunk_type)
        f.write(data)
        f.write(binascii.crc32(chunk_type + data).to_bytes(4, 'big'))

    chunk(
        b'IHDR',
        width.to_bytes(4, 'big') + height.to_bytes(4, 'big') + b'\x08\x06\x00\x00\x00',
    )
    chunk(b'IDAT', zlib.compress(raw, 9))
    chunk(b'IEND', b'')

print(f'created {path}')
