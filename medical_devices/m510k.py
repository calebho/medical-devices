"""Module for downloading 510(k) premarketing notification data"""
import asyncio
import io
import os
import zipfile

from aiohttp import ClientSession
from datetime import datetime
from typing import List, Dict, Optional, Union
from urllib.parse import urlparse

M510K_URIS = {
    # 1996 - current
    'http://www.accessdata.fda.gov/premarket/ftparea/pmn96cur.zip',
    # 1991 - 1995
    'http://www.accessdata.fda.gov/premarket/ftparea/pmn9195.zip',
    # 1986 - 1990
    'http://www.accessdata.fda.gov/premarket/ftparea/pmn8690.zip',
    # 1981 - 1985
    'http://www.accessdata.fda.gov/premarket/ftparea/pmn8185.zip',
    # 1976 - 1980
    'http://www.accessdata.fda.gov/premarket/ftparea/pmn7680.zip',
}
M510K_DATA_DIR = 'data/510k'

TVal = Optional[Union[str, bool, datetime]]


async def gen_510k() -> List[Dict[str, TVal]]:
    if not os.path.exists(M510K_DATA_DIR):
        os.makedirs(M510K_DATA_DIR, mode=0o755)
    async with ClientSession() as session:
        data = await asyncio.gather(*(gen_one_510k(session, uri)
                                      for uri in M510K_URIS))
    devices: List[Dict[str, TVal]] = []
    for item in data:
        devices.extend(item)
    return devices


async def gen_one_510k(
        session: ClientSession,
        uri: str,
) -> List[Dict[str, TVal]]:
    path = urlparse(uri).path
    zipname = os.path.basename(path)
    base_fname = zipname[:-4] + '.txt'
    fname = os.path.join(M510K_DATA_DIR, base_fname)
    if not os.path.exists(fname):
        try:
            r = await session.get(uri, raise_for_status=True)
        except Exception:
            return []
        else:
            b = await r.read()
            buf = io.BytesIO(b)
            with zipfile.ZipFile(buf) as z:
                z.extractall(path=M510K_DATA_DIR)

    devices = []
    with open(fname, errors='ignore') as f:
        headers = f.readline().strip().split('|')
        for line in f:
            values = line.strip().split('|')
            device: Dict[str, TVal] = {}
            for header, value in zip(headers, values):
                if value == '':
                    device[header] = None
                elif value in {'Y', 'N'}:
                    device[header] = True if value == 'Y' else False
                else:
                    try:
                        device[header] = datetime.strptime(value, '%m/%d/%Y')
                    except ValueError:
                        device[header] = value
            devices.append(device)
    return devices
