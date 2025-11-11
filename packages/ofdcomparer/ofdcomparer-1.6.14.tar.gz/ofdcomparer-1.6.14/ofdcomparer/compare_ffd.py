# coding: utf-8
import base64
import dataclasses
import inspect
import logging
import traceback
import warnings
from typing import List, Optional, Union

from ofdcomparer import ofd_cri_atol
from ofdcomparer.allure_helper import attach_compare_results
from ofdcomparer.dto10 import DTO10Helper
from ofdcomparer.ofd_helper import OfdHelper
from ofdcomparer.tags_fn import tags
from ofdcomparer.utils import Utils, DictModifier


class GetFdFnError(Exception):
    def __init__(self, message='Ошибка получения документа из ФН'):
        super().__init__(message)
        self.message = message


class GetFdOfdError(Exception):
    def __init__(self, message='Ошибка получения документа из ОФД'):
        super().__init__(message)
        self.message = message


class ComparerOfd:
    def __init__(self, dto10: DTO10Helper):

        self.DTO10: DTO10Helper = dto10
        self.OfdHelper = OfdHelper(dto10)
        self.utils = Utils(self.DTO10)
        self.dict_modifier = DictModifier()

        # Конечный результат обработки
        self.result = {}

        # Белый лист (проверка отключена)
        self.__white_list = ["fiscalDocumentType", "qr", "short"]

        self.__cast_methods = {
            "BYTE": self.__cast_byte,
            "INT16": self.__cast_int16,
            "INT32": self.__cast_int32,
            "VLN": self.__cast_vln,
            "FPD": self.__cast_fpd,
            "STRING": self.__cast_string,
            "COINS": self.__cast_coins,
            "UNIXTIME": self.__cast_unixtime,
            "FVLN": self.__cast_fvln,
            "STLV": self.__cast_stlv,
            "ENUM": self.__cast_enum,
            "SET": self.__cast_set,
            "BITS": self.__cast_bits,
            "BYTES": self.__cast_bytes,
        }

        self.etalon_value = None
        self.comparable_value = None

    def compare_etalon_fn_ofd(self, etalon: dict, changes: dict = None,
                              fd: int = None, ofd: str = 'taxcom',
                              print_result: bool = False,
                              rnm: str = None, fn: str = None) -> bool:
        """
        Метод сравнивает эталон с ФД в ФН, затем ФД в ФН с ФД в ОФД.
        params:
        etalon: dict - Эталонный ФД
        changes: dict - Список изменений
        fd: int - Номер ФД
        ofd: str - ОФД
        print_result: bool - печатает результаты сравнения
        """
        logging.info("Сравнение ФД, ЭТАЛОН : ФН : ОФД")
        logging.debug(f"{inspect.currentframe().f_code.co_name} < {etalon=} {changes=} {fd}")
        if not self.compare_etalon_fn(etalon=etalon, changes=changes, fd=fd, print_result=print_result):
            return False
        if not self.compare_fn_ofd(etalon=etalon, changes=changes, fd=fd, ofd=ofd,
                                   print_result=print_result, rnm=rnm, fn=fn):
            return False
        return True

    def compare_etalon_fn(self, etalon: dict, changes: dict = None,
                          fd: int = None, print_result: bool = False) -> bool:
        """
        Метод сравнивает эталон с ФД в ФН.
        params:
        etalon: dict - Эталонный ФД
        changes: dict - Список изменений (None удаляются, остальные изменяются)
        fd: int - Номер ФД
        print_result: bool - печатает результаты сравнения
        """
        logging.info("Сравнение ФД, ЭТАЛОН : ФН : ОФД")
        logging.debug(f"{inspect.currentframe().f_code.co_name} < {etalon=} {changes=} {fd=}")
        # очистка предыдущих результатов сравнения
        self.clear()
        if bool(changes):
            # подготовка эталона (удаление и изменение полей)
            etalon = self.dict_modifier.change_values_in_dict(etalon, changes)
        comparable = self.DTO10.get_fd_from_fn(fd if fd is not None else self.DTO10.get_last_fd_number())
        if comparable is None:
            raise GetFdFnError
        logging.info("Сравнение ФД, ЭТАЛОН : ФН")
        self.compare(etalon=etalon,
                     comparable=comparable)
        self.output_result_to_log()
        if print_result:
            self.print_result()
        attach_compare_results(result=self.result, name="Результат сравнения ФД. ЭТАЛОН - ФН")
        if self.is_have_failed():
            return False
        return True

    def compare_fn_ofd(self, etalon: dict, changes: dict = None,
                       fd: int = None, ofd: str = 'taxcom',
                       print_result: bool = False,
                       rnm: str = None, fn: str = None, fd_type: str = None) -> bool:
        """
        Метод сравнивает эталон с ФД в ФН, затем ФД в ФН с ФД в ОФД.
        params:
        etalon: dict - Эталонный ФД
        changes: dict - Список изменений
        fd: int - Номер ФД
        ofd: str - ОФД
        print_result: bool - печатает результаты сравнения
        """
        logging.info("Сравнение ФД, ФН : ОФД")
        logging.debug(f"{inspect.currentframe().f_code.co_name} < {etalon=} {changes=} {fd=}")

        # очистка предыдущих результатов сравнения
        self.clear()
        if bool(changes):
            etalon = self.dict_modifier.change_values_in_dict(etalon, changes)

        self.DTO10.wait_for_sent_all_fd()

        comparable = self.OfdHelper.get_fd_from_ofd(fd=fd, ofd=ofd, rnm=rnm, fn=fn, fd_type=fd_type)
        if comparable is None:
            raise GetFdOfdError
        logging.info("Сравнение ФД, ОФД : ФН")
        self.compare(etalon=etalon,
                     comparable=comparable)
        self.output_result_to_log()
        if print_result:
            self.print_result()
        attach_compare_results(result=self.result, name="Результат сравнения ФД. ЭТАЛОН - ФН")
        if self.is_have_failed():
            return False
        return True

    # TODO удалить это
    def compare_last_fd_in_fn_and_ofd(
            self, changes: dict = None, rnm=None, fn=None, fd=None
    ) -> bool:
        """
        Сравнивает последние документы в ФН и ОФД.
        modif_fd_number - опционально, добавляет смещение в номер сравниваемого документа.
        """
        warnings.warn(
            "compare_last_fd_in_fn_and_ofd is deprecated and will be removed in a future version. Please use "
            "compare_etalon_fn_ofd instead.",
            DeprecationWarning,
            stacklevel=2
        )
        logging.debug(f"{inspect.currentframe().f_code.co_name} < {changes=} {rnm=} {fn=} {fd=}")
        logging.info("Сравнение ФД, ФН : ОФД")
        self.clear()
        if rnm is None:
            rnm = self.DTO10.registrationNumber
        if fn is None:
            fn = self.DTO10.fnSerial
        if fd is None:
            fd = self.DTO10.get_fd_from_fn(self.DTO10.get_last_fd_number())
            if fd is None:
                raise GetFdFnError
        if bool(changes):
            fd = self.dict_modifier.change_values_in_dict(fd, changes)
        self.DTO10.wait_for_sent_all_fd()
        self.compare_tags(rnm=rnm, fn=fn, fd=fd)
        self.output_result_to_log()
        if self.is_have_failed():
            return False
        return True

    # TODO удалить это
    def compare_tags(
            self, modif_fd_number: Optional[int] = 0, rnm=None, fn=None, fd=None
    ) -> bool:
        warnings.warn(
            "compare_last_fd_in_fn_and_ofd is deprecated and will be removed in a future version. Please use "
            "compare_etalon_fn_ofd instead.",
            DeprecationWarning,
            stacklevel=2
        )
        logging.debug(f"{inspect.currentframe().f_code.co_name} < {modif_fd_number=} {rnm=} {fn=} {fd=}")
        self.clear()
        try:
            for _ in range(200):
                fd_number = self.DTO10.get_last_fd_number()
                if fd_number != None:
                    break

            # fd = self.Receipt.read_document_from_fn()
            if not rnm or not fn or not fd_number:
                return False
            fd_ofd = ofd_cri_atol.get_fd_from_cri_ofd(
                reg_number=rnm, fn=fn, fd_number=fd_number
            )
            self.compare(etalon=fd, comparable=fd_ofd)
            return True
        except Exception as e:
            logging.error(f"compare() error: {e}")
            traceback.print_exc()
            return False

    def compare(self, comparable: dict, etalon: dict) -> bool:
        """
        Сравнение по тегам ФД из ФН и ОФД
        """
        logging.info(f"{inspect.currentframe().f_code.co_name} < {comparable=} {etalon=}")
        for key in etalon:
            if key in comparable:
                if key in self.__white_list:
                    continue
                try:
                    self.etalon_value = etalon[key]
                    self.comparable_value = comparable[key]
                    if tags[key]["Type"] == "STLV":
                        self.__cast_stlv(
                            key=str(key),
                            comparable=self.comparable_value,
                            etalon=self.etalon_value,
                        )
                        continue
                    self.__cast_to_one_type(
                        key=str(key),
                        comparable=self.comparable_value,
                        etalon=self.etalon_value,
                    )
                except TypeError as e:
                    logging.error(f"Exception: {e}")
                    logging.error(f"params: tag = {key}")
                    traceback.print_exc()
                except Exception as e:
                    logging.error(f"Exception: {e}")
                    logging.error(
                        f"params: tag = {key}, etalon = {etalon[key]} ,comparable = {comparable[key]}"
                    )
                    traceback.print_exc()
                if self.comparable_value == self.etalon_value:
                    self.__message_pass(key, self.comparable_value, self.etalon_value)
                else:
                    self.__message_fail(key, self.comparable_value, self.etalon_value)
            else:
                self.__message_not_found(key, self.etalon_value)
        logging.debug(f"result: {self.result=}")
        return True

    def output_result_to_log(self) -> None:
        """
        Выводит результат сравнения в лог
        """
        if not self.result:
            logging.error("Результат сравнения пуст")
        else:
            for tag in self.result:
                if not self.result[tag][1] == "___WHITE_LIST___":
                    logging.info(
                        f"{self.result[tag][1]} | {self.result[tag][2]} | etalon {self.result[tag][4]} | "
                        f"compared {self.result[tag][3]} | {self.result[tag][5]}"
                    )

    def print_result(self) -> None:
        """
        Печатает результат сравнения
        """
        if not self.result:
            logging.error("Результат сравнения пуст")
        else:
            for tag in self.result:
                if not self.result[tag][1] == "___WHITE_LIST___":
                    print(
                        f"{self.result[tag][1]} | {self.result[tag][2]} | etalon {self.result[tag][4]} | "
                        f"compared {self.result[tag][3]} | {self.result[tag][5]}"
                    )

    def calc_result(self):
        """
        Считает результаты сравнения тегов, и формирует отчет по количествам.
        """
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        test_result = {tag: 0 for tag in ["passed", "skipped", "not_founded", "failed"]}
        if not self.result:
            logging.error("Результат сравнения пуст")
            return None
        for tag in self.result:
            if self.result[tag][1] == "+++PASS+++":
                test_result["passed"] += 1
            if self.result[tag][1] == "__SKIP__":
                test_result["skipped"] += 1
            if self.result[tag][1] == "===NOT_FOUND===":
                test_result["not_founded"] += 1
            if self.result[tag][1] == "---FAIL---":
                test_result["failed"] += 1
        logging.debug(f"{inspect.currentframe().f_code.co_name} > {test_result=}")
        return test_result

    def is_have_failed(self):
        """
        Проверяет, есть ли в результатах сравнения проваленные сравнения тегов или если тег у сравниваемого не обнаружен.
        Если результат хоть одного из этих параметров не равен 0, то вернет True.
        """
        logging.debug("is_have_failed()")
        if not self.result:
            logging.error("Результат сравнения пуст")
            return True
        test_result = self.calc_result()
        if test_result["failed"] != 0 or test_result["not_founded"] != 0:
            logging.debug("is_have_failed(): True")
            return True
        logging.debug("is_have_failed(): False")
        logging.info("ФД совпали")
        return False

    def clear(self):
        """
        Очистка результата сравнения
        """
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.result = {}
        return True

    def __cast_to_one_type(self, key, etalon, comparable):
        """
        Приводит значения одинаковых типов тегов к единой форме представления.
        Например, если один тег в копейках, а другой в рублях.
        """
        if tags[key]["Type"] in self.__cast_methods:
            key_method = tags[key]["Type"]
            if not self.__cast_methods[key_method](key, etalon, comparable):
                return False

    def __cast_byte(self, key, etalon, comparable):
        """
        Приводит к одному виду тип тегов BYTE
        """
        if comparable == 0 or "0":
            self.comparable_value = False
        if comparable == 1 or "1":
            self.comparable_value = True
        if etalon == 0 or "0":
            self.etalon_value = False
        if etalon == 1 or "1":
            self.etalon_value = True
        return True

    def __cast_int16(self, key, etalon, comparable):
        """
        Приводит к одному виду тип тегов INT16
        """
        self.etalon_value = int(etalon)
        self.comparable_value = int(comparable)
        return True

    def __cast_int32(self, key, etalon, comparable):
        """
        Приводит к одному виду тип тегов INT32
        """
        self.etalon_value = int(etalon)
        self.comparable_value = int(comparable)
        return True

    def __cast_vln(self, key, etalon, comparable):
        """
        Приводит к одному виду тип тегов VLN
        """
        return True

    def __cast_fpd(self, key, etalon, comparable):
        """
        Приводит к одному виду тип тегов FPD
        """
        if comparable == etalon:
            return True
        if self.__is_base64(comparable):
            self.comparable_value = base64.b64decode(comparable).hex().upper()
        return True

    def __cast_string(
            self, key: str, etalon: Union[str, List[str]], comparable: Union[str, List[str]]
    ) -> bool:
        """
        Приводит к одному виду тип тегов STRING

        Аргументы:
        - key: Ключ тега (не используется в методе)
        - etalon: Значение эталона, может быть строкой или списком строк
        - comparable: Значение для сравнения, может быть строкой или списком строк

        Возвращает:
        - bool: True, если приведение типа выполнено успешно
        """
        if isinstance(etalon, list):
            # Если etalon - список, применяем strip() к каждому элементу списка
            self.etalon_value = [value.strip() for value in etalon]

        if isinstance(comparable, list):
            # Если comparable - список, применяем strip() к каждому элементу списка
            self.comparable_value = [value.strip() for value in comparable]

        if isinstance(etalon, str):
            # Если etalon - строка, применяем strip() к ней
            self.etalon_value = etalon.strip()

        if isinstance(comparable, str):
            # Если comparable - строка, применяем strip() к ней
            self.comparable_value = comparable.strip()

        if isinstance(etalon, list) and isinstance(comparable, str):
            # Если etalon - список, а comparable - строка,
            # применяем strip() к первому элементу etalon
            self.etalon_value = etalon[0].strip()

        if isinstance(comparable, list) and isinstance(etalon, str):
            # Если comparable - список, а etalon - строка,
            # применяем strip() к первому элементу comparable
            self.comparable_value = comparable[0].strip()

        return True

    def __cast_coins(self, key, etalon, comparable):
        """
        Приводит к одному виду тип тегов COINS
        """
        etalon = float(etalon)
        comparable = float(comparable)
        if etalon > comparable:
            self.etalon_value = etalon / 100
            self.comparable_value = float(comparable)
        if comparable > etalon:
            self.comparable_value = comparable / 100
            self.etalon_value = float(etalon)
        return True

    def __cast_unixtime(self, key, etalon, comparable):
        """
        Приводит к одному виду тип тегов UNIXTIME
        """
        self.etalon_value = self.__remove_timezone(data=etalon)
        self.comparable_value = self.__remove_timezone(data=comparable)
        return True

    def __cast_fvln(self, key, etalon, comparable):
        """
        Приводит к одному виду тип тегов FVLN
        """
        etalon = str(etalon).strip()
        comparable = str(comparable).strip()
        try:
            self.etalon_value = float(etalon)
            self.comparable_value = float(comparable)
        except ValueError:
            try:
                self.etalon_value = int(etalon)
                self.comparable_value = int(comparable)
                return True
            except ValueError:
                traceback.print_exc()
                return False
        return True

    def __cast_stlv(self, key, etalon, comparable):
        """
        Приводит к одному виду тип тегов STLV
        """
        if not self.__expand_stlv(etalon=etalon, comparable=comparable, key=key):
            return False
        return True

    def __cast_enum(self, key, etalon, comparable):
        """
        Приводит к одному виду тип тегов ENUM
        """
        return True

    def __cast_set(self, key, etalon, comparable):
        """
        Приводит к одному виду тип тегов SET
        """
        return True

    def __cast_bits(self, key, etalon, comparable):
        """
        Приводит к одному виду тип тегов BITS
        """
        return True

    def __cast_bytes(self, key, etalon, comparable):
        """
        Приводит к одному виду тип тегов BYTES
        """
        if comparable == etalon:
            return True
        if self.__is_base64(comparable):
            self.comparable_value = base64.b64decode(comparable).hex().upper()
        return True

    def __expand_stlv(self, key, comparable, etalon):
        """
        Итерируется по составному тегу, и к каждому внутреннему тегу применяет метод compare()
        """
        if self.__is_list(comparable, etalon):
            if not isinstance(comparable, list) and isinstance(etalon, list):
                comparable = [comparable]
            elif isinstance(comparable, list) and not isinstance(etalon, list):
                etalon = [etalon]
            count = 0
            for i in range(len(etalon)):
                count += 1
                self.compare(comparable=comparable[i], etalon=etalon[i])
            return True
        if isinstance(comparable, dict) and isinstance(etalon, dict):
            self.compare(comparable=comparable, etalon=etalon)
            return True
        return False

    def __is_list(self, comparable, etalon):
        """
        Проверяет, является ли хоть одно из значений списком.
        """
        if isinstance(comparable, list) or isinstance(etalon, list):
            return True
        else:
            return False

    def __remove_timezone(self, data):
        """
        Удаляет таймзону из UNIXTIME значения
        """
        if "+" in data:
            return data.split("+")[0]
        return data

    def __append_to_result(self, status, message, key, comparable, etalon):
        """
        Добавление в итоговый результат
        """
        try:
            if not key in self.__white_list:
                self.result[len(self.result) + 1] = (
                    status,
                    message,
                    key,
                    comparable,
                    etalon,
                    tags[str(key)]["Name"],
                )
                return True
            self.result[len(self.result) + 1] = (
                True,
                "___WHITE_LIST___",
                key,
                comparable,
                etalon,
            )
            return True
        except Exception as e:
            logging.error(
                f"{inspect.currentframe().f_code.co_name} [ERROR] {status=} {message=} {key=} {comparable} {etalon}")
            logging.error(f"{inspect.currentframe().f_code.co_name} Exception: {e}")
            traceback.print_exc()
            return False

    def __message_pass(self, key, comparable, etalon):
        """
        Добавление в итоговый лист положительный результат сравнения
        """
        if not self.__append_to_result(True, "+++PASS+++", key, comparable, etalon):
            return False
        return True

    def __message_fail(self, key, comparable, etalon):
        """
        Добавление в итоговый лист отрицательный результат сравнения
        """
        if not self.__append_to_result(False, "---FAIL---", key, comparable, etalon):
            return False
        return True

    def __message_not_found(self, key, etalon):
        """
        Добавление в итоговый лист неудавшееся сравнение
        """
        if not self.__append_to_result(False, "===NOT_FOUND===", key, "None", etalon):
            return False
        return True

    def __message_error(self, key, comparable, etalon):
        """
        Добавление в итоговый лист сообщение об ошибке в обработке тега
        """
        if not self.__append_to_result(False, "[ERROR]", key, comparable, etalon):
            return False
        return True

    def __message_skip(self, key, comparable, etalon):
        """
        Добавление в итоговый лист сообщения о пропуске обработки тега
        """
        if not self.__append_to_result(True, "__SKIP__", key, comparable, etalon):
            return False
        return True

    @staticmethod
    def __is_base64(value):
        try:
            base64.b64decode(value, validate=True)
            return True
        except base64.binascii.Error:
            return False
