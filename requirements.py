import sys

PY2 = True if sys.version_info[0] == 2 else False
PY3 = not PY2

REQUIREMENTS = [
    "msgpack==0.5.6",
    "msgpack-numpy==0.4.1",
    "Pillow<6.0.0",
    "requests>=2.2.1",
    "setuptools==36.5.0",
    "six>=1.3.0",
]

# shim for futures support
if PY2:
    REQUIREMENTS.append("futures>=3.0.0")
    REQUIREMENTS.append("numpy<1.17")
else:
    REQUIREMENTS.append("numpy>=1.14.1")
