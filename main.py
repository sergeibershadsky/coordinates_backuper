import asyncio
import os
import time

import httpx
from httpx import HTTPError
from loguru import logger

from classes import UploadInfo
from decorators import tries
from exceptions import TooManyTriesException
from notifier import notify_handler

COORDINATES_URL = "https://www.marsruty.ru/krasnodar/gps.txt"
TIMEOUT = int(os.environ.get("TIMEOUT", 5))

Y_DISK_API_URL = "https://cloud-api.yandex.net/v1/disk/resources/upload"
Y_DISK_FOLDER = 'coordinates'
Y_DISK_TOKEN = os.environ.get('Y_DISK_TOKEN')
Y_DISK_AUTH_HEADERS = {'Authorization': f'OAuth {Y_DISK_TOKEN}'}

logger.add(notify_handler, level="ERROR")


@tries(times=2)
async def collect() -> str:
    async with httpx.AsyncClient() as client:
        logger.info('Получаем координаты')
        response = await client.get(COORDINATES_URL)
        response.raise_for_status()
        logger.success('Координаты получены ')
        return response.text


@tries(times=5, delay=3.0)
async def backup(data: str, timestamp: int) -> None:
    async with httpx.AsyncClient(headers=Y_DISK_AUTH_HEADERS) as client:
        logger.info('Записываем в Я.Диск')
        upload_info_response = await client.get(
            Y_DISK_API_URL,
            params={'path': f'/{Y_DISK_FOLDER}/gps.txt{timestamp}'}
        )
        upload_info_response.raise_for_status()
        upload_info = UploadInfo(**upload_info_response.json())
        if upload_info.method == 'PUT':
            backup_response = await client.put(upload_info.href, data=data)
            backup_response.raise_for_status()
        elif upload_info.method == 'POST':
            backup_response = await client.post(upload_info.href, data=data)
            backup_response.raise_for_status()
        else:
            logger.error('Метод загрузки не реализован {}', upload_info.method)
        logger.success('Координаты записанны')


async def collect_and_backup() -> None:
    while True:
        try:
            fetch_info = await collect()
            ts = int(time.time())
            await backup(fetch_info, ts)
        except HTTPError as e:
            logger.error('Ошибка отправки запроса: {}', e)
        except TooManyTriesException as e:
            logger.error(e)
        finally:
            logger.info(f'Ждем {TIMEOUT} сек')
            await asyncio.sleep(TIMEOUT)


if __name__ == '__main__':
    try:
        asyncio.run(collect_and_backup())
    except KeyboardInterrupt:
        logger.info('Выходим')
