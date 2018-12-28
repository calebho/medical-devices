"""Module for downloading medical devices data from the FDA"""
import asyncio
import json
import os
import requests
import sys

from aiohttp import ClientSession
from typing import Dict, List, Optional, NoReturn

GUDID_DATA_DIR = 'data/gudid/'
GUDID_URI = 'https://accessgudid.nlm.nih.gov/api/v2/devices/implantable/list.json'
GUDID_TOTAL_PAGES_KEY = 'X-Total-Pages'


def log_fatal(err: str) -> NoReturn:
    print(err, file=sys.stderr)
    sys.exit(1)


async def gudid():
    """Get the devices from the GUDID database"""
    r = requests.head(GUDID_URI)
    if r.status_code != requests.codes.ok:
        log_fatal(f'Got status code {r.status_code} from endpoint {GUDID_URI}')
    try:
        value = r.headers[GUDID_TOTAL_PAGES_KEY]
        num_pages = int(value)
    except KeyError:
        log_fatal(
            f"Entry '{GUDID_TOTAL_PAGES_KEY}' does not exist in header response"
        )
    except ValueError:
        log_fatal(
            f"Could not coerce '{GUDID_TOTAL_PAGES_KEY}' with value '{value}'")

    async with ClientSession() as session:
        pages = await gen_gudid_pages(session, num_pages)
    devices = []
    for page in pages:
        devices.extend(page['devices'])
    return devices


async def gen_gudid_pages(
        session: ClientSession,
        num_pages: int,
) -> List[Dict[str, str]]:
    dicts = await asyncio.gather(*(gen_gudid_page_json(session, page_num)
                                   for page_num in range(1, num_pages + 1)))
    return [d for d in dicts if d is not None]


async def gen_gudid_page_json(
        session: ClientSession,
        page_num: int,
) -> Optional[Dict[str, str]]:
    if not os.path.exists(GUDID_DATA_DIR):
        os.makedirs(GUDID_DATA_DIR, mode=0o755)
    fname = os.path.join(GUDID_DATA_DIR, f'{page_num}.json')
    try:
        with open(fname) as f:
            return json.load(f)
    except FileNotFoundError:
        params = {'page': page_num}
        try:
            r = await session.get(
                GUDID_URI, params=params, raise_for_status=True)
        except Exception:
            return None
        else:
            obj = await r.json()
            with open(fname, 'w') as f:
                json.dump(obj, f)
            return obj


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    devices = loop.run_until_complete(gudid())
    print(len(devices))
