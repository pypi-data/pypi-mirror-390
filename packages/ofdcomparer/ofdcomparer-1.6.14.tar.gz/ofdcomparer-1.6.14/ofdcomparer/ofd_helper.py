import inspect
import logging

from ofdcomparer.dto10 import DTO10Helper
from ofdcomparer.ofd_cri_atol import get_fd_from_cri_ofd
from ofdcomparer.ofd_taxcom import get_fd_from_taxcom


class OfdNotValidError(Exception):
    def __init__(self, message='Ошибка. Выбранный ОФД недопустим'):
        super().__init__(message)
        self.message = message


class OfdVariableIsNone(Exception):
    def __init__(self, message='Ошибка. None аргумент недопустим'):
        super().__init__(message)
        self.message = message


class OfdHelper:
    def __init__(self, dto10: DTO10Helper):
        self.DTO10: DTO10Helper = dto10
        self.valid_ofd = ('taxcom', 'cri')
        self.ofd_fd_getters = {
            'taxcom': get_fd_from_taxcom,  # (reg_number: str, fn: str, fd_number: int, timeout: int = 60)
            'cri': get_fd_from_cri_ofd,  # (reg_number: str, fn: str, fd_number: int, timeout: int = 60)
        }

    def get_fd_from_ofd(self, fd: int, ofd: str, timeout: int = 60,
                        rnm: str = None, fn: str = None, fd_type: str = None):
        logging.info("Получение ФД от ОФД")
        logging.debug(f"{inspect.currentframe().f_code.co_name} < {fd=} {ofd=}")
        if ofd not in self.ofd_fd_getters.keys():
            raise OfdNotValidError
        self.DTO10.get_registration_data()
        if rnm is not None:
            reg_number = rnm
        else:
            reg_number = self.DTO10.registrationNumber
        if reg_number is None:
            raise OfdVariableIsNone(message="reg_number is None (регистрационный номер ККТ)")
        self.DTO10.get_fn_info()
        if fn is not None:
            fn = fn
        else:
            fn = self.DTO10.fnSerial
        if fn is None:
            raise OfdVariableIsNone(message="fn is None (номер ФН)")
        return self.ofd_fd_getters[ofd](reg_number=reg_number, fn=fn, fd_number=fd, timeout=timeout, fd_type=fd_type)
