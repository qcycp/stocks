import csv
import datetime
import js2py
import os
import pyquery
import random
import re
import requests
import time
import urllib.parse
from config import DATADIR
from app.foundation import logger

proxies = list()

def getProxy():
    global proxies
    if len(proxies) == 0:
        getProxies()
    proxy = random.choice(proxies)
    logger.debug(f'getProxy: {proxy}')
    proxies.remove(proxy)
    logger.debug(f'getProxy: {len(proxies)} proxies is unused.')
    return proxy

def reqProxies(hour):
    global proxies
    proxies = proxies + getProxiesFromProxyNova()
    proxies = proxies + getProxiesFromGatherProxy()
    proxies = proxies + getProxiesFromFreeProxyList()
    proxies = list(dict.fromkeys(proxies))
    logger.debug(f'reqProxies: {len(proxies)} proxies is found.')

def getProxies():
    global proxies
    now = datetime.datetime.now()
    hour = f'{now:%Y%m%d}'
    filename = os.path.join(DATADIR, f'proxies-{hour}.csv')
    filepath = f'{filename}'
    if os.path.isfile(filepath):
        logger.info(f'getProxies: {filename} exists.')
        logger.warning(f'getProxies: {filename} is loading...')
        with open(filepath, 'r', newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                proxy = row['Proxy']
                proxies.append(proxy)
        logger.success(f'getProxies: {filename} is loaded.')
    else:
        logger.info(f'getProxies: {filename} does not exist.')
        reqProxies(hour)
        logger.warning(f'getProxies: {filename} is saving...')
        with open(os.path.join(DATADIR, filepath), 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Proxy'
            ])
            for proxy in proxies:
                writer.writerow([
                    proxy
                ])
        logger.success(f'getProxies: {filename} is saved.')

def getProxiesFromProxyNova():
    proxies = []
    countries = [
        'tw',
        'jp',
        'kr',
        'id',
        'my',
        'th',
        'vn',
        'ph',
        'hk',
        'uk',
        'us'
    ]
    for country in countries:
        url = f'https://www.proxynova.com/proxy-server-list/country-{country}/'
        logger.debug(f'getProxiesFromProxyNova: {url}')
        logger.warning(f'getProxiesFromProxyNova: downloading...')
        response = requests.get(url)
        if response.status_code != 200:
            logger.debug(f'getProxiesFromProxyNova: status code is not 200')
            continue
        logger.success(f'getProxiesFromProxyNova: downloaded.')
        d = pyquery.PyQuery(response.text)
        table = d('table#tbl_proxy_list')
        rows = list(table('tbody:first > tr').items())
        logger.warning(f'getProxiesFromProxyNova: scanning...')
        for row in rows:
            tds = list(row('td').items())
            if len(tds) == 1:
                continue
            js = row('td:nth-child(1) > abbr').text()
            js = 'let x = %s; x' % (js[15:-2])
            ip = js2py.eval_js(js).strip()
            port = row('td:nth-child(2)').text().strip()
            proxy = f'{ip}:{port}'
            proxies.append(proxy)
        logger.success(f'getProxiesFromProxyNova: scanned.')
        logger.debug(f'getProxiesFromProxyNova: {len(proxies)} proxies is found.')
        time.sleep(1)
    return proxies

def getProxiesFromGatherProxy():
    proxies = []
    countries = [
        'Taiwan',
        'Japan',
        'United States',
        'Thailand',
        'Vietnam',
        'Indonesia',
        'Singapore',
        'Philippines',
        'Malaysia',
        'Hong Kong'
    ]
    for country in countries:
        url = f'http://www.gatherproxy.com/proxylist/country/?c={urllib.parse.quote(country)}'
        logger.debug(f'getProxiesFromGatherProxy: {url}')
        logger.warning(f'getProxiesFromGatherProxy: downloading...')
        response = requests.get(url)
        if response.status_code != 200:
            logger.debug(f'getProxiesFromGatherProxy: status code is not 200')
            continue
        logger.success(f'getProxiesFromGatherProxy: downloaded.')
        d = pyquery.PyQuery(response.text)
        scripts = list(d('table#tblproxy > script').items())
        logger.warning(f'getProxiesFromGatherProxy: scanning...')
        for script in scripts:
            script = script.text().strip()
            script = re.sub(r'^gp\.insertPrx\(', '', script)
            script = re.sub(r'\);$', '', script)
            script = json.loads(script)
            ip = script['PROXY_IP'].strip()
            port = int(script['PROXY_PORT'].strip(), 16)
            proxy = f'{ip}:{port}'
            proxies.append(proxy)
        logger.success(f'getProxiesFromGatherProxy: scanned.')
        logger.debug(f'getProxiesFromGatherProxy: {len(proxies)} proxies is found.')
        time.sleep(1)
    return proxies

def getProxiesFromFreeProxyList():
    proxies = []
    url = 'https://free-proxy-list.net/'
    logger.debug(f'getProxiesFromFreeProxyList: {url}')
    logger.warning(f'getProxiesFromFreeProxyList: downloading...')
    response = requests.get(url)
    if response.status_code != 200:
        logger.debug(f'getProxiesFromFreeProxyList: status code is not 200')
        return
    logger.success(f'getProxiesFromFreeProxyList: downloaded.')
    d = pyquery.PyQuery(response.text)
    trs = list(d('table#proxylisttable > tbody > tr').items())
    logger.warning(f'getProxiesFromFreeProxyList: scanning...')
    for tr in trs:
        tds = list(tr('td').items())
        ip = tds[0].text().strip()
        port = tds[1].text().strip()
        proxy = f'{ip}:{port}'
        proxies.append(proxy)
    logger.success(f'getProxiesFromFreeProxyList: scanned.')
    logger.debug(f'getProxiesFromFreeProxyList: {len(proxies)} proxies is found.')
    return proxies