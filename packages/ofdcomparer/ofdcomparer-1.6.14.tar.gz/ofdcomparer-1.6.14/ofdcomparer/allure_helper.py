import allure


def attach_compare_results(result: dict, name: str):
    lines = []
    for key, value in result.items():
        if len(value) < 6:
            continue
        _, status, code, compared, etalon, message = value
        line = f"{status} | {code} | etalon {etalon} | compared {compared} | {message}"
        lines.append(line)
    report = "\n".join(lines)
    allure.attach(report, name=name, attachment_type=allure.attachment_type.TEXT)


