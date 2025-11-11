import json
import logging
import re
import sys
import time
from datetime import datetime

DOSSymbols = (
    ' !"#$%&`()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~'
    " АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмноп                                              "
    "  рстуфхцчшщъыьэюяЁё          №   "
)

KKTSymbols = (
    ' !"#№%&`()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~'
    " АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмноп                                              "
    "  рстуфхцчшщъыьэюяЁё€         $   "
)

InKKTSymbols = (
    'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ !"#№%&`()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^'
    "_`abcdefghijklmnopqrstuvwxyz{|}~ абвгдежзийклмнопрстуфхцчшщъыьэюя$€-                            "
    "                                                 Ёё            \t "
)

OutKKTSymbols = (
    '         \t                       !"#№%&`()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^'
    "_`abcdefghijklmnopqrstuvwxyz{|}~ АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмноп              "
    "                                  рстуфхцчшщъыьэюяЁё€       - $   "
)


# noinspection PyPep8Naming
def DictToStr(Dictionary):
    return json.dumps(Dictionary, ensure_ascii=False, encoding="utf-8")


def ByteToDOS(byte):
    return DOSSymbols[byte - 0x20]


def DOSToByte(char):
    for i in range(256):
        if DOSSymbols[i] == char:
            return i + 0x20
    return 0x20


def ByteToKKTSymbols(char):
    return KKTSymbols[char]


def ByteToInKKTSymbols(char):
    return InKKTSymbols[char]


def KKTSymbToByte(char):
    for i in range(256):
        if KKTSymbols[i] == char:
            return i + 0x20
    return 0x20


def ArrayToStr(array):
    result = ""
    for code in array:
        result += chr(code)
    return result


def StringToBytes(string):
    result = ""
    for CHR in string:
        result = result + HexToStr(DOSToByte(CHR))
    return result


def StringToBytesKKT(string):
    result = ""
    for CHR in string:
        result = result + HexToStr(KKTSymbToByte(CHR))
    return result


def BytesKKTInToString(array):
    result = ""
    for Byte in array:
        result += InKKTSymbols[Byte]
    return result


def ArrayToHexString(array):
    result = ""
    space = False
    for Byte in array:
        result += HexToStr(Byte, space)
        space = True
    return result


def StringToHex(string):
    """
    Перевод строки ответа в hex массив
    """
    parsed = [(hex(c)) for c in bytearray(string)]
    return str(parsed)


def DataToHexString(string):
    result = ""
    for CHR in bytearray(string, encoding="utf-8"):
        result = result + HexToStr(CHR)
    return result


def DateTimeToUnix(date_time):
    return int(time.mktime(date_time.timetuple()))


def UnixTimeToDateTime(unix_time):
    return datetime.fromtimestamp(unix_time)


def UnixTimeToString(unix_time):
    return UnixTimeToDateTime(unix_time).strftime("%d.%m.%Y %H:%M:%S")


def string_to_unix_time_bytes(str_date_time):
    """str_date_time строка вида 'YYYY.MM.DD hh:mm:ss'"""
    dt = datetime.strptime(str_date_time, "%Y.%m.%d %H:%M:%S")
    unixtime = DateTimeToUnix(dt)
    return int(unixtime).to_bytes(length=4, byteorder=sys.byteorder)


def NumberToBytes(number, count_of_bytes):
    result = ""
    for i in range(count_of_bytes):
        result = result + HexToStr(number & 0xFF)
        number = number >> 8
    return result


def NumberToArray(number, count_of_bytes):
    result = []
    for i in range(count_of_bytes):
        result.append(number & 0xFF)
        number = number >> 8
    if count_of_bytes == 0:
        while number > 0:
            result.append(number & 0xFF)
            number = number >> 8
    return result


def DateTimeToUnixBytes(date_time):
    return NumberToBytes(DateTimeToUnix(date_time), 4)


def DateTimeToUnixArray(date_time):
    return NumberToArray(DateTimeToUnix(date_time), 4)


def HexToStr(Integer, print_space: bool = True):
    if print_space:
        space = " "
    else:
        space = ""
    return space + ("%X" % Integer).rjust(2, "0")


def ByteStrToList(string):
    array = []
    for byte in string.split(" "):
        array.append(int(byte, 16))
    return array


def StructToList(struct):
    return list(struct.unpack("{}B".format(len(struct)), struct))


def StructToHexString(struct):
    result = ""
    space = False
    for Byte in StructToList(struct):
        result += HexToStr(Byte, space)
        space = True
    return result


def ArrayToHexString(array):
    result = ""
    space = False
    for Byte in array:
        result += HexToStr(Byte, space)
        space = True
    return result


def HexStringToString_InP5(
    hex_string,
):  # декодер из кодировки ККТ- позволяет читать данные в привычной кодировке
    result = ""
    hex_string_arr = hex_string.split(" ")
    for hexSymbol in hex_string_arr:
        b = bytes.fromhex(hexSymbol)
        result += b.decode("cp866")
    return result


def StringToHexString(
    string,
):  # кодировщик в кодировку ККТ (просто вводить аргументы для команды через ';')
    string = str(string)
    result = ""
    for char in string:
        b = bytes(char, "cp866")
        result += bytes.hex(b).upper()
        result += " "
    return result.strip()


def StringSpaceSplit(string, step=2):
    return " ".join([string[i : i + step] for i in range(0, len(string), step)])


def Crc16Table():
    crctable = []
    for i in range(0x100):
        r = (i & 0xFF) << 8
        for j in range(8):
            if r & (1 << 15):
                r = (r << 1) ^ 0x1021
            else:
                r = r << 1
        crctable.append(r & 0xFFFF)
    return crctable


def CRC16_CCITT(p_buf):
    t_ans = 0xFFFF
    table = Crc16Table()
    for BYTE in p_buf:
        t_ans = ((t_ans << 8) & 0xFFFF) ^ table[((t_ans >> 8) & 0xFFFF) ^ BYTE]
    return t_ans


def CRC16_CCITT_XModem(p_buf):
    t_ans = 0x0000
    table = Crc16Table()
    for BYTE in p_buf:
        t_ans = ((t_ans << 8) & 0xFFFF) ^ table[((t_ans >> 8) & 0xFFFF) ^ BYTE]
    return t_ans


# фунцкия вычисляет контрольное число для 10-значного ИНН, требуется 9 символов, строки длиннее обрезаются
def CalcINN10(inn10):
    inn10 = str(inn10)
    if len(inn10) < 9:
        inn10 = inn10.zfill(9)
    a = []
    for i in range(9):
        a.append(int(inn10[i]))
    c = (
        2 * a[0]
        + 4 * a[1]
        + 10 * a[2]
        + 3 * a[3]
        + 5 * a[4]
        + 9 * a[5]
        + 4 * a[6]
        + 6 * a[7]
        + 8 * a[8]
    )
    c = (c % 11) % 10
    return inn10[:9] + str(c)


def CalcINN12(inn12):
    """
    фунцкия вычисляет контрольное число для 12-значного ИНН, требуется 10 символов, строки длиннее обрезаются
    """
    inn12 = str(inn12)
    if len(inn12) < 10:
        inn12 = inn12.zfill(10)
    a = []
    for i in range(10):
        a.append(int(inn12[i]))
    c1 = (
        7 * a[0]
        + 2 * a[1]
        + 4 * a[2]
        + 10 * a[3]
        + 3 * a[4]
        + 5 * a[5]
        + 9 * a[6]
        + 4 * a[7]
        + 6 * a[8]
        + 8 * a[9]
    )
    c1 = (c1 % 11) % 10
    c2 = (
        3 * a[0]
        + 7 * a[1]
        + 2 * a[2]
        + 4 * a[3]
        + 10 * a[4]
        + 3 * a[5]
        + 5 * a[6]
        + 9 * a[7]
        + 4 * a[8]
        + 6 * a[9]
        + 8 * c1
    )
    c2 = (c2 % 11) % 10
    return inn12[:10] + str(c1) + str(c2)


# фунцкия вычисляет ИНН с контрольными числами, длина строки без пробелов определяет ИНН 10 или ИНН 12
def CalcINN(inn):
    inn = str(inn).replace(" ", "")
    if len(inn) == 10:
        return CalcINN10(inn)
    if len(inn) == 12:
        return CalcINN12(inn)


# фунцкия вычисляет РНМ по ИНН и ЗН, требуется 10 символов РНМ, строки длиннее обрезаются
def CalcRNM(full_serial_number, inn12, rnm):
    full_serial_number = str(full_serial_number)[:20]
    inn12 = str(inn12)[:12].strip()
    rnm = str(rnm)[:10]
    if len(rnm) < 10:
        rnm = rnm.zfill(10)
    if len(inn12) < 12:
        inn12 = inn12.zfill(12)
    if len(full_serial_number) < 20:
        full_serial_number = full_serial_number.zfill(20)
    p_buf = []
    for CHAR in bytearray(str(rnm) + inn12 + str(full_serial_number), encoding="utf-8"):
        p_buf.append(CHAR)
    c = CRC16_CCITT(p_buf)
    c = str(c).zfill(6)
    return rnm + c


def GetBit(byte, number):
    return ((1 << number) & byte) >> number


def SetBit(byte, number):
    return byte | (1 << number)


# def SendMsg(Data):
#     try:
#         sock = socket.socket()
#         sock.connect(('localhost', 7567))
#         sock.send(Data)
#         sock.settimeout(30)
#         data = sock.recv(1024)
#         if data == 'OK':
#             logging.debug('OK - Succesfully sent socket data ' + Data)
#         else:
#             logging.debug('"{}"'.format(data))
#         sock.close()
#         time.sleep(5)
#         del sock
#     except:
#         logging.debug('BAD (time out!) - not sent socket data ' + Data)


def SendMsg(data):
    try:
        file = open(r"C:\ProgramData\ATOL\OT\emr.sok", "a", encoding="utf-8")
        file.write(data + "\n")
        file.close()
    except Exception as e:
        logging.debug(e)


def End(code, driver=None):
    if driver is not None and not driver.gAutoTest:
        return
    try:
        time.sleep(2)
        SendMsg("END " + code)
        time.sleep(2)
        exit()
    except Exception as e:
        logging.debug("Не удалось отправить данные скрипта", e)
        pass


def valid_IP(ip_adress):
    octets = str(ip_adress).split(".")
    if len(octets) != 4:
        return False
    for octet in octets:
        # noinspection PyBroadException
        try:
            if int(octet) > 255:
                return False
        except Exception:
            return False
    return True


def valid_MAC(mac):
    octets = str(mac).split(":")
    if len(octets) != 6:
        octets = str(mac).split("-")
    if len(octets) != 6:
        return False
    for octet in octets:
        # noinspection PyBroadException
        try:
            if int(octet, 16) > 255:
                return False
        except Exception:
            return False
    return True


# noinspection PyPep8Naming
class Hex:
    # StrHex:           '404132'
    # StrHexSpace:      '40 41 32'
    # List:             [0x40, 0x41, 0x32]
    # Bytes (Symbols):  '@A2'

    Array = []

    def clear(self):
        self.Array = []

    def setHexData(self, data, _bytes=None):
        self.Array = self.__HexData__(data, _bytes)

    def addHexData(self, data, _bytes=None):
        self.Array += self.__HexData__(data, _bytes)

    def setSymbolsData(self, data, _bytes=None):
        self.Array = self.__HexData__(data, _bytes=True)

    def addSymbolsData(self, data, _bytes=None):
        self.Array += self.__HexData__(data, _bytes=True)

    def setIntData(self, data, LE=True, BytesCount=None):
        self.Array = self.__IntData__(data, LE, BytesCount)

    def addIntData(self, data, LE=True, BytesCount=None):
        self.Array += self.__IntData__(data, LE, BytesCount)

    def __IntData__(self, data, LE=True, BytesCount=None):
        Result = []
        if BytesCount is None:
            while data > 0:
                Result.append(data & 0xFF)
                data = data >> 8
        else:
            for i in range(BytesCount):
                Result.append(data & 0xFF)
                data = data >> 8
        if not LE:
            Result.reverse()
        return Result

    def __HexData__(self, data, _bytes):
        Result = []
        if type(data) == list:
            Result = data
        elif type(data) == str:
            if not _bytes:
                if re.match("^[A-Fa-f0-9]*$", data) is not None:
                    Index = 0
                    while Index < len(data):
                        Result.append(int(data[Index : Index + 2], 16))
                        Index += 2
                    return Result
                elif re.match("^[A-Fa-f0-9 ]*$", data) is not None:
                    for byte in data.split(" "):
                        if len(byte) > 2:
                            Result = []
                            return Result
                            # Result.append(int(byte, 16))
                    return Result
            for symbol in bytearray(data, encoding="utf-8"):
                Result.append(symbol)
        return Result

    def toList(self):
        return self.Array

    def toBytes(self):
        Result = ""
        for elem in self.Array:
            Result += chr(elem)
        return Result

    def toSymbols(self):
        return self.toBytes()

    def toStrHex(self):
        Result = ""
        for elem in self.Array:
            Result += "{Hex:02X}".format(Hex=elem)
        return Result

    def toStrHexSpace(self):
        Result = ""
        for elem in self.Array:
            Result += "{Hex:02X} ".format(Hex=elem)
        return Result.strip()

    def __str__(self):
        return self.toStrHexSpace()


if __name__ == "__main__":
    h = Hex()
    h.setIntData(0)
    # logging.debug(StringToHexString(''))
