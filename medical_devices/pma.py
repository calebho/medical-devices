"""Module for downloading Premarket Approval Application (PMA) data"""
import io
import requests
import os
import zipfile

from datetime import datetime
from typing import List, Dict, Optional, Union

PMA_DATA_DIR = 'data/pma/'
PMA_URI = 'http://www.accessdata.fda.gov/premarket/ftparea/pma.zip'

TVal = Optional[Union[str, bool, datetime]]


def get_pma() -> List[Dict[str, TVal]]:
    if not os.path.exists(PMA_DATA_DIR):
        os.makedirs(PMA_DATA_DIR, mode=0o755)
    fname = os.path.join(PMA_DATA_DIR, 'pma.txt')
    if not os.path.exists(fname):
        r = requests.get(PMA_URI)
        b = io.BytesIO(r.content)
        with zipfile.ZipFile(b) as z:
            z.extractall(path=PMA_DATA_DIR)

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


if __name__ == '__main__':
    from pprint import pprint
    devices = get_pma()
    print(len(devices))
    pprint(devices[0])
