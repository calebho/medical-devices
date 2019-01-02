"""Module for downloading medical devices data from the Global Unique Device
Identification Database (GUDID)
"""
import io
import time
import os
import zipfile

from aiohttp import ClientSession, ClientTimeout
from datetime import datetime
from typing import AsyncIterator, Dict, Optional, Union

GUDID_DATA_DIR = 'data/gudid/'
DEVICE_DATA_FNAME = 'device.txt'

TVal = Optional[Union[str, bool, datetime]]


async def gen_gudid() -> AsyncIterator[Dict[str, TVal]]:
    """Get the devices from the GUDID"""
    if not os.path.exists(GUDID_DATA_DIR):
        os.makedirs(GUDID_DATA_DIR, mode=0o755)
    async with ClientSession(timeout=ClientTimeout(None)) as session:
        await gen_gudid_data(session)

    fname = os.path.join(GUDID_DATA_DIR, get_gudid_data_dir(),
                         DEVICE_DATA_FNAME)
    with open(fname) as f:
        headers = f.readline().strip().split('|')
        for line in f:
            values = line.strip().split('|')
            device: Dict[str, TVal] = {}
            for header, value in zip(headers, values):
                if value == '':
                    device[header] = None
                elif value in {'true', 'false'}:
                    device[header] = True if value == 'true' else False
                else:
                    try:
                        device[header] = datetime.strptime(value, '%Y-%m-%d')
                    except ValueError:
                        device[header] = value
            yield device


async def gen_gudid_data(session: ClientSession) -> None:
    dirname = os.path.join(GUDID_DATA_DIR, get_gudid_data_dir())
    if os.path.exists(dirname):
        return

    uri = get_gudid_data_uri()
    r = await session.get(uri, raise_for_status=True)
    buf = io.BytesIO()
    async for b in r.content.iter_any():
        buf.write(b)
    os.makedirs(dirname)
    with zipfile.ZipFile(buf) as z:
        z.extractall(path=dirname)


def get_gudid_data_uri() -> str:
    return f'https://accessgudid.nlm.nih.gov/release_files/download/{get_gudid_data_dir()}.zip'


def get_gudid_data_dir() -> str:
    date_str = time.strftime('%Y%m') + '01'
    return f'AccessGUDID_Delimited_Full_Release_{date_str}'
