import logging
import time

import requests

from ofdcomparer.helpers import convert_fn_format, convert_receipt_format


def get_fd_from_cri_ofd(reg_number: str, fn: str, fd_number: int, timeout: int = 60, fd_type: str = None):
    """
    Получение ФД от CRI-OFD-ATOL
    """
    logging.debug(f"get_fd_from_cri_ofd() < fn_number {fn}, fd {fd_number}")
    if fn is None:
        logging.debug(f"get_fd_from_cri_ofd() > None")
        return None
    headers = {"Content-Type": "application/json"}
    data = {"reg_number": reg_number, "fn": fn, "fd_number": fd_number}

    url = "http://cri-ofd.atol.ru:50010/get_fd"

    response = requests.get(url, headers=headers, params=data, allow_redirects=True)
    fd_cri_ofd = None
    logging.debug(f"headers: {headers} \ndata: {data}")
    try:
        start_time = time.time()
        while not time.time() - start_time > timeout:
            response = requests.get(
                url, headers=headers, params=data, allow_redirects=True
            )
            logging.info(f"cri request {url},{headers} {data}")
            logging.info("response: %s", response)
            time.sleep(1)
            if response.status_code == 200:
                fd_cri_ofd = response.json()
                fn_format_doc = convert_fn_format(convert_receipt_format(fd_cri_ofd)[0], fd_type=fd_type)
                logging.debug(f"fn_format_doc: {fn_format_doc}")

                logging.info("formated document")
                logging.info(fn_format_doc)
                return fn_format_doc
    except requests.exceptions.RequestException as e:
        raise Exception(f"[ERROR] with get fd from ofd: {e}")
