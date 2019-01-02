"""Module for downloading medical devices data from the Global Unique Device
Identification Database (GUDID)
"""
import asyncio
import io
import time
import os
import zipfile

from aiohttp import ClientSession, ClientTimeout
from typing import Dict, List

GUDID_DATA_DIR = 'data/gudid/'
DEVICE_DATA_FNAME = 'device.txt'


async def gen_gudid() -> List[Dict[str, str]]:
    """Get the devices from the GUDID"""
    if not os.path.exists(GUDID_DATA_DIR):
        os.makedirs(GUDID_DATA_DIR, mode=0o755)
    async with ClientSession(timeout=ClientTimeout(None)) as session:
        await gen_gudid_data(session)

    fname = os.path.join(GUDID_DATA_DIR, DEVICE_DATA_FNAME)
    data = []
    with open(fname) as f:
        headers = f.readline().strip().split('|')
        for line in f:
            values = line.strip().split('|')
            data.append(dict(zip(headers, values)))
    return data


async def gen_gudid_data(session: ClientSession) -> None:
    if os.path.exists(os.path.join(GUDID_DATA_DIR, DEVICE_DATA_FNAME)):
        return

    uri = get_gudid_data_uri()
    r = await session.get(uri, raise_for_status=True)
    buf = io.BytesIO()
    async for b in r.content.iter_any():
        buf.write(b)
    with zipfile.ZipFile(buf) as z:
        z.extractall(path=GUDID_DATA_DIR)


def get_gudid_data_uri() -> str:
    date_str = time.strftime('%Y%m') + '01'
    return f'https://accessgudid.nlm.nih.gov/release_files/download/AccessGUDID_Delimited_Full_Release_{date_str}.zip'


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    devices = loop.run_until_complete(gen_gudid())
    print(len(devices))
