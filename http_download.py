#!/usr/bin/python

"""
http re_download file from last save point

"""
import os
import sys
import time
import random
import logging
import requests
import threading
import configparser


def file_size(file_name):
    if os.path.isfile(file_name):
        return os.path.getsize(file_name)
    else:
        return 0


def log_download_speed():
    time_now = time.time()
    while time.time() - time_now < keep_log_time:
        # filename = r'F:\http_downloadfile' + '\\' + url_random.split('/')[-1]
        file_size_before = file_size(filename)  # this is where the bug comes from
        time.sleep(time_bin)
        file_size_after = file_size(filename)
        download_speed = (file_size_after - file_size_before) / (time_bin * 1000)
        logger.info('download_speed is {} Kbps'.format(download_speed))


def download(url, chunk_size=65535):
    downloaded = 0  # data already download
    # filename = r'F:\http_downloadfile' + '\\' + url.split('/')[-1]
    if os.path.isfile(filename):
        downloaded = file_size(filename)
        logger.info('File already exists,Send resume request after {} Bytes'.format(downloaded))
    # Update request header to add 'Range'
    headers = {}
    if downloaded:
        headers['Range'] = 'bytes={}-'.format(downloaded)
    head_url = requests.head(url, headers=headers)
    res = requests.get(url, headers=headers, stream=True, timeout=15)
    mode = 'wb'
    temp = head_url.headers.get('Content-Length')
    if temp is not None:
        content_len = int(temp)
        logger.info('{} bytes to downloaded.'.format(content_len))
        # check if server supports range feature,and works as expected
        if res.status_code == 206:
            # contetnge is in format: 'bytes 32654 -4368852/4566666',check if  it starts from  where we requested
            content_range = res.headers.get(
                'content-range')  # if file is already downloaded,it will return 'bytes */4566666'
            if content_range and int(content_range.split(' ')[-1].split('-')[0]) == downloaded:
                mode = 'ab+'
        if res.status_code == 416:
            logger.info('File download already complete.')
            return
    else:
        logger.info('this website does not support redownload .')

    with open(filename, mode) as fd:
        for chunk in res.iter_content(chunk_size):
            fd.write(chunk)
            downloaded += len(chunk)
            # logger.info('{} bytes downloaded.'.format(downloaded))
    logger.info('Download complete.')


def keep_conention():
    # res = requests.get(url, headers=headers, stream=True, timeout=15)
    is_connetion_ok = 0
    try:
        keep_download_func()
        return
    except:
        logger.error('Download Error,download stopped.')
        temp_count = 1
        time_break = time.time()
        while (temp_count < 15) or (time.time() - time_break < 300):
            try:
                request.urlopen(url, timeout=Timeout)
                logger.info('Reconnection Success. Try to redownload file from last point.')
                is_connetion_ok = 1
                break
            except:
                temp_count += 1
                continue

        if is_connetion_ok:
            logger.info('Http download continue...')
            keep_conention()  # what will happen if domnload complete?
        else:
            logger.error('Try to reconnet but fail')
            return


def keep_download_func():
    # filename = 'F:\http_downloadfile' + '\\' + url_random.split('/')[-1]
    time_now = time.time()
    while time.time() - time_now < keep_download_time:
        logger.info('Start download...')
        download(url_random)
    #logger.info('Download Complete !')
    # if os.path.isfile(filename):
    #     os.remove(filename)
    #     logger.info('The file has been deleted')
    # else:
    #     logger.info('The file does not exist')


if __name__ == '__main__':
    # config file
    config = configparser.ConfigParser()
    config.read(r'F:\http_downloadfile\config.ini', encoding='utf-8')
    url_list = [j for i, j in config.items('url')]
    url_random = url_list[random.randint(0, len(url_list) - 1)]

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filename=r'F:\http_downloadfile\log\log.txt')
    logger = logging.getLogger(__name__)
    logger.info('Start print log')

    keep_download_time = 3600
    keep_log_time = 3600
    time_bin = 30

    filename = r'F:\http_downloadfile' + '\\' + url_random.split('/')[-1]

    thread1 = threading.Thread(name='keep_download_file', target=keep_conention)
    thread2 = threading.Thread(name='keep_caculate_downloadspeed', target=log_download_speed)

    thread1.start()
    time.sleep(2)
    thread2.start()
    thread1.join()
    thread2.join()
    print('-----------All Thread over----------------')
