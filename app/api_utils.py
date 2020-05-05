import chardet
import requests
import time
import traceback
from app.foundation import logger

def decode_content(data):
    txt = None
    # 對 HTTP / HTTPS 回應的二進位原始內容，使用chardet進行編碼判斷
    det = chardet.detect(data.content)
    try:
        # 若判斷結果信心度超過 0.5
        if det['confidence'] > 0.5:
            #logger.info("encoding: %s" % det['encoding'])
            if det['encoding'] == 'big-5' or det['encoding'] == 'Big5':
                # cp950包含big5
                txt = data.content.decode('big5')
            else:
                txt = data.content.decode(det['encoding'])
        else:
            # 若判斷信心度不足，則嘗試使用 UTF-8 解碼
            txt = data.content.decode('utf-8')
    except:
        logger.error(traceback.format_exc())
    return txt

def get(url, headers=None):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
    retry = 0
    while retry < 3:
        try:
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code != 200:
                retry += 1
                time.sleep(60)
                continue

            data = decode_content(res)
            return data
        except:
            retry += 1
            logger.error(traceback.format_exc())
    return None