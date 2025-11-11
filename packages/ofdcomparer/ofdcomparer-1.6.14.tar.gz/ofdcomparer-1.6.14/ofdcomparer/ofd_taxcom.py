import logging
import os
import time
import base64
import requests


def get_token():
    """
    Получение токена от Такском ОФД
    """
    integrator_id = os.getenv("TAXCOM_INTEGRATOR_ID")
    login = os.getenv('TAXCOM_LOGIN')
    password = os.getenv('TAXCOM_PASSWORD')

    if not integrator_id:
        raise ValueError("TAXCOM_INTEGRATOR_ID environment variable is not set")
    if not login:
        raise ValueError("TAXCOM_LOGIN environment variable is not set")
    if not password:
        raise ValueError("TAXCOM_PASSWORD environment variable is not set")

    headers = {
        "Content-Type": "application/json",
        "Integrator-ID": integrator_id.strip(),
    }
    url = "http://api-tlk-ofd.taxcom.ru/API/v2/Login"
    session_token = None
    try:
        response = requests.post(url, allow_redirects=False, verify=False)
    except requests.exceptions.RequestException as e:
        raise Exception(f"[ERROR] with get token from ofd: {e}")
    try:
        if response.status_code == 301:
            response = requests.post(
                response.headers["Location"], headers=headers, json={"login": login.strip(),
                                                                     "password": password.strip()}, verify=False
            )
            session_token = response.json()["sessionToken"]
    except requests.exceptions.RequestException as e:
        raise Exception(f"[ERROR] with get token from ofd: {e}")
    return session_token


def get_fd_from_taxcom(reg_number: str, fn: str, fd_number: int, timeout: int = 60, fd_type: str = None):
    """
    Получение ФД от Такском ОФД
    """
    logging.debug(f"get_fd_from_taxcom() < fn_number {fn}, fd {fd_number}")
    if fn is None:
        logging.debug(f"get_fd_from_ofd() > None")
        return None
    headers = {"Session-Token": get_token()}
    data = {"fn": str(fn), "fd": str(fd_number)}
    url = "https://api-tlk-ofd.taxcom.ru/API/v2/DocumentInfo"
    logging.debug(f"headers: {headers} \ndata: {data}")
    try:
        start_time = time.time()
        while not time.time() - start_time > timeout:
            response = requests.get(
                url, headers=headers, params=data, allow_redirects=True, verify=False
            )
            logging.info("response: %s", response)
            time.sleep(1)
            if response.status_code == 200:
                fd_taxcom = response.json()["document"]
                return fd_taxcom
    except requests.exceptions.RequestException as e:
        raise Exception(f"[ERROR] with get fd from ofd: {e}")

