import asyncio
import os
import aiohttp

import json

import requests
from dotenv import load_dotenv

from . import app

load_dotenv()

AUTH_HEADER = {
    'Authorization': f'OAuth {DISK_TOKEN}'
}
API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
DISK_INFO_URL = f'{API_HOST}{API_VERSION}/disk/'
DISK_TOKEN = os.environ.get('DISK_TOKEN')
REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'

async def async_upload_files_to_disk(files):
    if files is not None:
        tasks = []
        async with aiohttp.ClientSession() as session:
            for file in files:
                tasks.append(
                    asyncio.ensure_future(
                        upload_file_and_get_url(session, file)
                    )
                )
            urls = await asyncio.gather(*tasks)
        return urls



async def upload_file_and_get_url(session, file):
    payload = {
        'path': f'app:/{file.name}',
        'overwrite': 'True'
    }
    async with session.post(
            REQUEST_UPLOAD_URL,
            headers=AUTH_HEADER,
            params=payload,
    ) as response:
        upload_url = await response.json()['href']



    async with session.post(
            SHARING_LINK,
            headers={
                'Authorization': AUTH_HEADER,
                'Content-Type': 'application/json',
            },
            json={'path': path}
    ) as response:
        data = await response.json()
        if 'url' not in data:
            data = data['error']['shared_link_already_exists']['metadata']
        url = data['url']
        url = url.replace('&dl=0', '&raw=1')
    return url