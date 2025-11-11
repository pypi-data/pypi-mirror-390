import json
import logging
from datetime import datetime, timedelta


def compare_json_structure(json_template_path, fn_doc_from_fn):
    with open(json_template_path, "r", encoding="utf-8") as f:
        json_file_data = f.read()
    json_template_formated_data = json.loads(json_file_data)

    keys1 = set(json_template_formated_data.keys())
    keys2 = set(fn_doc_from_fn.keys())

    key_differance = keys2.symmetric_difference(keys1)
    if key_differance:
        logging.error("Различия в ключах")
        for key in key_differance:
            if key not in keys2:
                logging.error(f"---FAILED--- key: {key} not in fn")
        return False

    logging.info("Ключи полностью совпадают с шаблонными")
    return True


def convert_fn_format(data, fd_type):
    str_tags = [
        "1018",
        "1226",
        "1016",
        "1041",
        "1075",
        "1073",
        "1037",
        "1264",
        "1171",
    ]
    int_tags = ["1213", "1040", "1135", "1179", "1038"]
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                convert_fn_format(value)

            elif key == "1016":
                data[key] = str(value)
            elif key == "1037":
                data[key] = str(value).zfill(16)
            elif key == "1262":
                data[key] = str(value).zfill(3)
            elif key == "1073":
                if isinstance(data[key], str):
                    data[key] = json.loads(data[key])
            elif key == "1074":
                if isinstance(data[key], str):
                    data[key] = json.loads(data[key])
            elif key == "1075":
                if isinstance(data[key], str):
                    data[key] = json.loads(data[key])
            elif key == "1077":
                hex_data = hex(data[key]).upper()[2:]
                if fd_type == "openShift":
                    data[key] = f"2304{hex_data}"
                elif fd_type == "receipt":
                    data[key] = f"3104{hex_data}"
                elif fd_type == "closeShift":
                    data[key] = f"2404{hex_data}"
            elif key == "1171":
                if isinstance(data[key], str):
                    data[key] = json.loads(data[key])
            elif key == "1178":
                data[key] = convert_time(data[key])
            elif key in int_tags:
                data[key] = int(value)
            elif key in str_tags:
                data[key] = str(value)
            elif isinstance(value, int):
                str_value = str(value)
                if len(str_value) > 2:
                    data[key] = str_value
            elif isinstance(value, str):
                strip_value = value.strip()
                data[key] = strip_value
    return data


def compare_dict(json_formated_data, variable_settings):
    if json_formated_data:
        for setting in variable_settings:
            if setting in list(json_formated_data.keys()):
                del json_formated_data[setting]
            elif "1059" in list(json_formated_data.keys()):
                if setting in json_formated_data["1059"][0]:
                    del json_formated_data["1059"][0][setting]
    return json_formated_data


def convert_time(input_time):
    dt = datetime.strptime(input_time, "%d.%m.%Y %H:%M:%S")
    dt -= timedelta(hours=3)
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def convert_receipt_format(data):
    def convert_value(value):
        if isinstance(value, str):
            parts = value.split(" ")
            if len(parts) > 0 and parts[0].isdigit():
                return int(parts[0])
        return value

    converted_data = []
    str_tags = [1226, 1074, 1075, 1073, 1171, 1223, 1654, 1264]

    for item in data:
        new_item = {}
        for tag_info in item["value"]:
            tag_name = tag_info["tag"]
            tag_value = tag_info["value"]

            if isinstance(tag_value, list):
                nested_dict = {}
                for nested_item in tag_value:
                    nested_tag_name = nested_item["tag"]
                    nested_tag_value = nested_item["value"]
                    if isinstance(nested_tag_value, list):
                        sub_nested_dict = {}
                        for sub_nested_item in nested_tag_value:
                            sub_nested_tag_name = sub_nested_item["tag"]
                            sub_nested_tag_value = sub_nested_item["value"]
                            if (
                                sub_nested_tag_name == 1012
                                or sub_nested_tag_name == 1098
                                or sub_nested_tag_name == 1178
                            ):
                                sub_nested_dict[
                                    str(sub_nested_tag_name)
                                ] = convert_time(sub_nested_tag_value)
                            elif sub_nested_tag_name == 1016:
                                sub_nested_dict[str(sub_nested_tag_name)] = str(
                                    sub_nested_tag_value
                                ).strip()
                            elif sub_nested_tag_name == 1262:
                                sub_nested_dict[str(sub_nested_tag_name)] = str(
                                    sub_nested_tag_value
                                ).zfill(3)
                            elif sub_nested_tag_name in str_tags:
                                sub_nested_dict[str(sub_nested_tag_name)] = [
                                    sub_nested_tag_value
                                ]  # Always format as a list
                            else:
                                sub_nested_dict[str(sub_nested_tag_name)] = (
                                    convert_value(sub_nested_tag_value).strip()
                                    if isinstance(
                                        convert_value(sub_nested_tag_value), str
                                    )
                                    else convert_value(sub_nested_tag_value)
                                )
                        nested_dict[str(nested_tag_name)] = sub_nested_dict
                    else:
                        if nested_tag_name == 1012 or nested_tag_name == 1098:
                            nested_dict[str(nested_tag_name)] = convert_time(
                                nested_tag_value
                            )
                        elif nested_tag_name == 1016:
                            nested_dict[str(nested_tag_name)] = str(
                                nested_tag_value
                            ).strip()
                        elif nested_tag_name == 1262:
                            nested_dict[str(nested_tag_name)] = str(
                                nested_tag_value
                            ).zfill(3)
                        elif nested_tag_name in str_tags:
                            nested_dict[str(nested_tag_name)] = [
                                nested_tag_value
                            ]  # Always format as a list
                        else:
                            nested_dict[str(nested_tag_name)] = (
                                convert_value(nested_tag_value).strip()
                                if isinstance(convert_value(nested_tag_value), str)
                                else convert_value(nested_tag_value)
                            )

                if str(tag_name) == "1059":
                    if "1059" in new_item:
                        new_item["1059"].append(nested_dict)
                    else:
                        new_item["1059"] = [nested_dict]
                else:
                    new_item[str(tag_name)] = nested_dict
            else:
                if tag_name == 1012 or tag_name == 1098:
                    new_item[str(tag_name)] = convert_time(tag_value)
                elif tag_name == 1016:
                    new_item[str(tag_name)] = str(tag_value).strip()
                elif tag_name == 1262:
                    new_item[str(tag_name)] = str(tag_value).zfill(3)
                elif tag_name in str_tags:
                    new_item[str(tag_name)] = [tag_value]  # Always format as a list
                else:
                    new_item[str(tag_name)] = (
                        convert_value(tag_value).strip()
                        if isinstance(convert_value(tag_value), str)
                        else convert_value(tag_value)
                    )

        converted_data.append(new_item)

    return converted_data
