Библиотека для сравнивания ФД из ФН и ОФД
## Установка библиотеки
```cmd
pip install ofdcomparer
```

#### Сравнивание документов
```python
from ofdcomparer.dto10 import DTO10Helper
from ofdcomparer.compare_ffd import ComparerOfd

dto10 = DTO10Helper()
comparer_ofd = ComparerOfd(dto10=dto10)

# эталонный офд
etalon = {
    "1018": "112233445573",
    "1020": 1,
    "1031": 0,
    "1037": "0000000001047959",
    "1041": "9999078945337305",
    "1054": 1,
    "1055": 1,
    "1059": [
        {
            "1023": 1,
            "1030": "НДС. Крем от бородавок \"Жабка\" 20%",
            "1043": 1,
            "1079": 1,
            "1199": 1,
            "1212": 1
        }
    ],
    "1081": 1,
    "1102": 0.17,
    "1209": 2,
    "1215": 0,
    "1216": 0,
    "1217": 0,
    "fiscalDocumentType": "receipt",
    "short": False
}

# Словарь изменений, необходимых внести в эталонный ФД перед сравнением
changes = {
    "1081": 0,  # сумма по чеку (БСО) безналичными
    "1031": 1,  # сумма по чеку (БСО) наличными
    "1054": 1,  # признак расчета (1 - приход)
    "1209": 4,  # ффд
    "1021": None,  # кассир
    "1037": None,  # регистрационный номер ККТ
    "1041": None,  # заводской номер фискального накопителя
    "1042": None,  # номер чека за смену
}

# получаем последний фискальный документ по номеру 
fd_from_fn = dto10.get_fd_from_fn(fd=dto10.get_last_fiscal_document_number())
# получаем ФД с ОФД по номеру ФН и РНМ и сравниваем с ФД с ФН
assert comparer_ofd.compare_etalon_fn_ofd(etalon=etalon, changes=changes, fd=fd_from_fn,
                              ofd='taxcom')
```

Для использования Таксом ОФД требуются переменные среды: TAXCOM_INTEGRATOR_ID, TAXCOM_LOGIN, TAXCOM_PASSWORD

