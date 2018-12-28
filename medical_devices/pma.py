"""Module for downloading Premarket Approval Application (PMA) data"""
import io
import requests
import os
import zipfile

from typing import List, Dict

PMA_DATA_DIR = 'data/pma/'
PMA_URI = 'http://www.accessdata.fda.gov/premarket/ftparea/pma.zip'


def get_pma() -> List[Dict[str, str]]:
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
            devices.append(dict(zip(headers, values)))
    return devices


if __name__ == '__main__':
    devices = get_pma()
    print(len(devices))
    print(devices[0])
