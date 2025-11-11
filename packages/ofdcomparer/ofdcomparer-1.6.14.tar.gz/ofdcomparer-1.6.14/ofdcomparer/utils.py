import json
import math
import os
from typing import Tuple
import logging

from ofdcomparer.dto10 import DTO10Helper

START_DIR = os.getcwd()
PROJECT_ROOT_DIR = os.path.dirname(__file__)


class Utils:

    def __init__(self, dto10: DTO10Helper):
        self.dto: DTO10Helper = dto10

    def save_to_files_all_fd_from_fn(self):
        last_fd = self.dto.get_last_fd_number()
        fd_fn = self.dto.get_fd_from_fn(
            fd=last_fd)
        folder_path = os.path.join(PROJECT_ROOT_DIR, 'test_data', 'raw')
        count = 0
        while count < last_fd:
            try:
                count += 1
                fd_fn = self.dto.get_fd_from_fn(count)
                logging.debug(fd_fn)
                logging.debug("COUNT: ", count)
                os.makedirs(folder_path, exist_ok=True)
                filepath = os.path.join(folder_path, f'{count}.json')
                logging.debug(filepath)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(str(fd_fn))
                logging.debug("OK")
            except Exception as e:
                logging.debug("ERROR: {}".format(e))

    def write_to_json(self, path, filename, data):
        try:
            filepath = os.path.join(START_DIR, path, filename)
            with open(filepath, 'x', encoding='utf-8') as f:
                json.dump(data, f)
            return True
        except:
            return False

    def remove_keys_from_json_files_recursively(self, keys: list, path: str):
        """
        Метод рекурсивно проходит по всем вложенным папкам в поисках .json файлов.
        В каждом файле удаляет ключи и значения заданные в параметрах.
        Например:
        keys_to_remove = ["1038",
                          "1040",
                          "1042",
                          "qr",
                          "1021",
                          "1012",
                          "1042",
                          "1077",
                          ]
        path = os.path.join('test_data', 'FFD_1_05', 'cash')
        operations.change_values_in_json_files_recursively(keys=keys_to_remove, path=path)
        """
        # Define the directory to traverse
        root_dir = os.path.join(START_DIR, path)

        # Traverse the directory tree and modify JSON files
        for subdir, dirs, files in os.walk(root_dir):
            for file in files:
                # Check if the file is a JSON file
                if file.endswith('.json'):
                    # Load the JSON data from the file
                    file_path = os.path.join(subdir, file)
                    logging.debug("file_path: ", file_path)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Delete the text-value pair from the JSON data
                    for key in keys:
                        if key in data:
                            del data[key]

                    # Write the modified JSON data back to the file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f)

    def change_values_in_json_files_recursively(self, keys: dict, path: str):
        """
        Метод рекурсивно проходит по всем вложенным папкам в поисках .json файлов.
        В каждом файле меняет значения у ключей заданных в параметрах.
        Например:
        keys = {
        "1031": 0,
        "1081": 1,
        }
        path = os.path.join('test_data', 'FFD_1_05', 'card')
        operations.change_values_in_json_files_recursively(keys=keys, path=path)
        """
        logging.debug("change_values_in_json_files_recursively()")
        logging.debug("keys: ", keys)
        logging.debug("path: ", path)
        # Define the directory to traverse
        root_dir = os.path.join(START_DIR, path)

        # Traverse the directory tree and modify JSON files
        for subdir, dirs, files in os.walk(root_dir):
            for file in files:
                # Check if the file is a JSON file
                if file.endswith('.json'):
                    # Load the JSON data from the file
                    file_path = os.path.join(subdir, file)
                    logging.debug("file_path: ", file_path)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Delete the text-value pair from the JSON data
                    for key in keys:
                        if key in data:
                            logging.debug("data[text]: ", data[key])
                            logging.debug("keys[text]: ", keys[key])
                            data[key] = keys[key]

                    # Write the modified JSON data back to the file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f)

    def change_values_in_dict(self, dict_needs_to_change: dict, changes: dict) -> dict:
        """
        Метод изменяет поданный словарь, согласно поданным параметрам (поиск с заменой).
        Если значение None, то удаляет ключ.
        Возвращает измененный словарь.
        """
        logging.debug("change_values_in_dict()")
        # Delete the text-value pair from the JSON data
        count = 0
        for key in changes:
            if key in dict_needs_to_change:
                if changes[key] is None:
                    dict_needs_to_change.pop(key)
                else:
                    dict_needs_to_change[key] = changes[key]
                count += 1
        if count > 0:
            logging.debug("change_values_in_dict(): Словарь подготовлен")
            return dict_needs_to_change
        else:
            logging.debug("change_values_in_dict(): В словаре нечего менять")

    def find_coordinates_by_vector(self, width, height, direction: int, distance: int, start_x: int, start_y: int) -> \
    Tuple[
        int, int]:
        """
        fill me
        """

        # Расчет конечной точки на основе направления и расстояния
        angle_radians = direction * (math.pi / 180)  # Преобразование направления в радианы
        dy = abs(distance * math.cos(angle_radians))
        dx = abs(distance * math.sin(angle_radians))

        if 0 <= direction <= 180:
            x = start_x + dx
        else:
            x = start_x - dx

        if 0 <= direction <= 90 or 270 <= direction <= 360:
            y = start_y - dy
        else:
            y = start_y + dy

        # Обрезка конечной точки до границ экрана
        x2 = (max(0, min(x, width)))
        y2 = (max(0, min(y, height)))

        return x2, y2

    def calculate_center_of_coordinates(self, coordinates: Tuple[int, int, int, int]) -> Tuple[int, int]:
        """
        Вычисляет центр координат для четырех точек.

        Аргументы:
        coordinates (Tuple[int, int, int, int]): Кортеж из четырех целочисленных значений координат: x1, y1, x2, y2.

        Возвращает:
        Tuple[int, int]: Кортеж из двух целочисленных значений, представляющих координаты центра.

        """
        # Распаковываем координаты из кортежа
        x1, y1, x2, y2 = coordinates

        # Вычисляем центр по оси x путем сложения x1 и x2, деленного на 2
        center_x = (x1 + x2) // 2

        # Вычисляем центр по оси y путем сложения y1 и y2, деленного на 2
        center_y = (y1 + y2) // 2

        # Возвращаем кортеж с центральными координатами (center_x, center_y)
        return center_x, center_y


class DictModifier:
    original_dict: dict
    modified_dict: dict
    changes: dict
    path: list

    def change_values_in_dict(self, original_dict, changes):
        self.modified_dict = {}
        self.original_dict = original_dict
        self.changes = changes
        return self.process_dict()

    def process_dict(self):
        # перебираем оригинальный словарь
        for k, v in self.original_dict.items():
            # если ключ в словаре изменений, то изменяем значение в оригинальном словаре
            if k in self.changes.keys():
                if self.changes[k] is not None:
                    self.modified_dict[k] = self.changes[k]
                    continue
            if not isinstance(v, list) and not isinstance(v, dict) and k not in self.changes.keys():
                self.modified_dict[k] = v
                continue
            if isinstance(v, dict):
                for k1, v1 in v.items():
                    if k1 in self.changes.keys():
                        v[k1] = self.changes[k]
                self.modified_dict[k] = v
            if isinstance(v, list):
                temp_list = []
                for el in v:
                    if not isinstance(el, dict):
                        temp_list = el
                        break
                    temp_dict = {}
                    for k2, v2 in el.items():
                        if k2 in self.changes.keys() and self.changes[k2] is not None:
                            temp_dict[k2] = self.changes[k2]
                            continue
                        if k2 not in self.changes.keys():
                            temp_dict[k2] = v2
                    temp_list.append(temp_dict)
                self.modified_dict[k] = temp_list

        return self.modified_dict
