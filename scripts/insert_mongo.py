#!/usr/bin/env python3
"""A script for downloading all the FDA data and inserting it into MongoDB.

There are 3 FDA data sources.
    1) Global Unique Device Identification Database (GUDID)
    2) Premarket Approvals (PMA)
    3) 510(k) Premarketing Notification (510k)
"""
import asyncio
import argparse
import sys

from ipaddress import ip_address
from typing import AsyncIterator, TypeVar, Tuple

try:
    from medical_devices.gudid import gen_gudid
    from medical_devices.m510k import gen_510k
    from medical_devices.pma import get_pma
except ImportError:
    print('Please install "medical_devices" first.', file=sys.stderr)
    sys.exit(1)

try:
    from pymongo import MongoClient
    from pymongo.database import Database
except ImportError:
    print('Please install "pymongo" first".', file=sys.stderr)
    sys.exit(1)

T = TypeVar('T')


class MyFormatter(
        argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter,
):
    pass


def my_ip_address(inp: str) -> str:
    if inp == 'localhost':
        return inp
    return str(ip_address(inp))


def positive_int(inp: str) -> int:
    return abs(int(inp))


def database_name(inp: str) -> str:
    if len(inp) == 0:
        raise ValueError('Database name cannot be empty')
    if inp[0] == '$':
        raise ValueError('Database name cannot start with "$"')
    if '.' in inp:
        raise ValueError('Database name cannot contain "."')
    return inp


async def aenumerate(
        iterator: AsyncIterator[T],
        start: int = 0,
) -> AsyncIterator[Tuple[int, T]]:
    idx = start
    async for x in iterator:
        yield idx, x
        idx += 1


async def insert_gudid(db: Database) -> None:
    print('Inserting GUDID data into Mongo. This may take a few minutes...')
    async for inserted, device in aenumerate(gen_gudid(), start=1):
        db.gudid.insert_one(device)
        if inserted % 100_000 == 0:
            print(f'Inserted {inserted:,}...')
    print('Done.')


async def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=MyFormatter)
    parser.add_argument(
        '--host',
        type=my_ip_address,
        help='The host running the Mongo daemon instance.',
        default='localhost')
    parser.add_argument(
        '--port',
        type=positive_int,
        help='The port bound to the Mongo daemon.',
        default=27017)
    parser.add_argument(
        '--name',
        help=
        'The name of the Mongo database. Cannot contain "." or begin with "$".',
        default='medical_devices',
        type=database_name)
    args = parser.parse_args()

    client = MongoClient(args.host, args.port)
    db = client[args.name]

    _, data_510k = await asyncio.gather(insert_gudid(db), gen_510k())

    print('Inserting 510k data into Mongo.')
    db['510k'].insert_many(data_510k)
    print('Done.')

    pma = get_pma()
    print('Inserting PMA data into Mongo.')
    db.pma.insert_many(pma)
    print('Done.')

    print('Finished inserting all data into Mongo.')


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
