from curl_cffi import requests
import zlib
import json
from .exceptions import ConstantError

CONSTANTS = {}

def decode_constants(data):
  try:
    decompressed = zlib.decompress(data, -zlib.MAX_WBITS)
  except zlib.error:
    decompressed = zlib.decompress(data)

  utf_str = decompressed.decode('utf-8')
  return json.loads(utf_str)


def init_constants(*, debug: bool = False):
  url = "https://hz-static-2.akamaized.net/assets/data/constants_json.data"
  r = requests.get(url, timeout=10, impersonate="chrome")
  r.raise_for_status()
  CONSTANTS.update(decode_constants(r.content))
  if not CONSTANTS:
    raise ConstantError("Failed to initialize constants.")
  if debug:
    with open('tests/data/constants.json', 'w', encoding='utf-8') as f:
      json.dump(CONSTANTS, f, ensure_ascii=False, indent=4)
