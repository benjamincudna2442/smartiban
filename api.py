from flask import Flask, request, jsonify
import random
import string
import logging
import pycountry
from collections import defaultdict

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

country_data = {
    "AL": {"length": 28, "bank_code_length": 8, "account_length": 16},
    "AD": {"length": 24, "bank_code_length": 8, "account_length": 12},
    "AT": {"length": 20, "bank_code_length": 5, "account_length": 11},
    "AZ": {"length": 28, "bank_codes": ["NABZ", "AIIB"], "account_length": 20},
    "BH": {"length": 22, "bank_codes": ["BBKU", "AUBB"], "account_length": 14},
    "BE": {"length": 16, "bank_code_length": 3, "account_length": 7, "check_digits_length": 2},
    "BA": {"length": 20, "bank_code_length": 3, "branch_code_length": 3, "account_length": 8, "check_digits_length": 2},
    "BR": {"length": 29, "bank_code_length": 8, "branch_code_length": 5, "account_length": 10, "account_type_length": 1, "owner_type_length": 1},
    "CR": {"length": 22, "bank_code_length": 4, "account_length": 14},
    "HR": {"length": 21, "bank_code_length": 7, "account_length": 10},
    "CY": {"length": 28, "bank_code_length": 8, "account_length": 16},
    "CZ": {"length": 24, "bank_code_length": 4, "prefix_length": 10, "account_length": 6},
    "DK": {"length": 18, "bank_code_length": 4, "account_length": 9, "check_digit_length": 1},
    "DO": {"length": 28, "bank_codes": ["BAGR", "BRES"], "account_length": 20},
    "EG": {"length": 29, "bank_code_length": 4, "branch_code_length": 4, "account_length": 17},
    "SV": {"length": 28, "bank_codes": ["CENR", "CUSC"], "account_length": 20},
    "EE": {"length": 20, "bank_code_length": 2, "branch_code_length": 2, "account_length": 11, "check_digit_length": 1},
    "FO": {"length": 18, "bank_code_length": 4, "account_length": 9, "check_digit_length": 1},
    "FI": {"length": 18, "bank_code_length": 6, "account_length": 7, "check_digit_length": 1},
    "FR": {"length": 27, "bank_code_length": 5, "branch_code_length": 5, "account_length": 11, "key_length": 2},
    "GE": {"length": 22, "bank_codes": ["NB", "BG"], "account_length": 16},
    "DE": {"length": 22, "bank_codes": ["50010517", "10000000", "20000000", "30000000", "37050198"], "account_length": 10},
    "GI": {"length": 23, "bank_codes": ["NWBK", "BARC"], "account_length": 15},
    "GR": {"length": 27, "bank_code_length": 4, "branch_code_length": 3, "account_length": 16},
    "GL": {"length": 18, "bank_code_length": 4, "account_length": 9, "check_digit_length": 1},
    "GT": {"length": 28, "bank_codes": ["TRAJ", "GTCO"], "account_length": 20},
    "HU": {"length": 28, "bank_code_length": 3, "branch_code_length": 4, "check_digit_length": 1, "account_length": 15, "second_check_digit_length": 1},
    "IS": {"length": 26, "bank_code_length": 4, "branch_code_length": 2, "identification_length": 6, "account_length": 10},
    "IE": {"length": 22, "bank_codes": ["AIBK", "BOFI"], "sort_code_length": 6, "account_length": 8},
    "IL": {"length": 23, "bank_code_length": 6, "account_length": 13},
    "IT": {"length": 27, "check_char": True, "bank_code_length": 5, "branch_code_length": 5, "account_length": 12},
    "JO": {"length": 30, "bank_codes": ["CBJO", "JIBA"], "branch_code_length": 4, "account_length": 18},
    "KZ": {"length": 20, "bank_code_length": 3, "account_length": 13},
    "XK": {"length": 20, "bank_code_length": 4, "account_length": 10, "check_digits_length": 2},
    "KW": {"length": 30, "bank_codes": ["CBKU", "GULB"], "account_length": 22},
    "LV": {"length": 21, "bank_codes": ["HABA", "UNLA"], "account_length": 13},
    "LB": {"length": 28, "bank_code_length": 4, "account_length": 20},
    "LI": {"length": 21, "bank_code_length": 5, "account_length": 12},
    "LT": {"length": 20, "bank_code_length": 5, "account_length": 11},
    "LU": {"length": 20, "bank_code_length": 3, "account_length": 13},
    "MK": {"length": 19, "bank_code_length": 3, "account_length": 10, "check_digits_length": 2},
    "MT": {"length": 31, "bank_codes": ["MALT", "MMEB"], "branch_code_length": 5, "account_length": 18},
    "MR": {"length": 27, "bank_code_length": 5, "branch_code_length": 5, "account_length": 11, "check_digits_length": 2},
    "MC": {"length": 27, "bank_code_length": 5, "branch_code_length": 5, "account_length": 11, "key_length": 2},
    "ME": {"length": 22, "bank_code_length": 3, "account_length": 13, "check_digits_length": 2},
    "NL": {"length": 18, "bank_codes": ["ABNA", "INGB", "RABO"], "account_length": 10},
    "NO": {"length": 15, "bank_code_length": 4, "account_length": 6, "check_digit_length": 1},
    "PK": {"length": 24, "bank_codes": ["SCBL", "HABB"], "account_length": 16},
    "PL": {"length": 28, "bank_code_length": 8, "account_length": 16},
    "PT": {"length": 25, "bank_code_length": 4, "branch_code_length": 4, "account_length": 13},
    "QA": {"length": 29, "bank_codes": ["QNBA", "DOHB"], "account_length": 21},
    "MD": {"length": 24, "bank_codes": ["AG", "VI"], "account_length": 18},
    "RO": {"length": 24, "bank_codes": ["AAAA", "BRDE"], "account_length": 16},
    "SM": {"length": 27, "check_char": True, "bank_code_length": 5, "branch_code_length": 5, "account_length": 12},
    "SA": {"length": 24, "bank_code_length": 2, "account_length": 18},
    "RS": {"length": 22, "bank_code_length": 3, "account_length": 13, "check_digits_length": 2},
    "SK": {"length": 24, "bank_code_length": 4, "prefix_length": 6, "account_length": 10},
    "SI": {"length": 19, "bank_code_length": 5, "branch_code_length": 3, "account_length": 8, "check_digits_length": 2},
    "ES": {"length": 24, "bank_code_length": 4, "branch_code_length": 4, "check_digits_length": 2, "account_length": 10},
    "SE": {"length": 24, "bank_code_length": 3, "account_length": 16, "check_digit_length": 1},
    "CH": {"length": 21, "bank_code_length": 5, "account_length": 12},
    "TL": {"length": 23, "bank_code_length": 3, "account_length": 16, "check_digits_length": 2},
    "TR": {"length": 26, "bank_code_length": 5, "reserved_length": 1, "account_length": 16},
    "UA": {"length": 29, "bank_code_length": 6, "account_length": 19},
    "AE": {"length": 23, "bank_code_length": 3, "account_length": 16},
    "GB": {"length": 22, "bank_codes": ["BARC", "LOYD", "NWBK", "HBUK"], "sort_code_length": 6, "account_length": 8},
    "VA": {"length": 22, "bank_code_length": 3, "account_length": 15},
    "VG": {"length": 24, "bank_codes": ["VPVG", "FCIB"], "account_length": 16}
}

def generate_numeric(length: int) -> str:
    return ''.join(str(random.randint(0, 9)) for _ in range(length))

def generate_alpha(length: int) -> str:
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))

def generate_alphanum(length: int) -> str:
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

def letter_to_number(c: str) -> str:
    return str(ord(c.upper()) - 55) if c.isalpha() else c

def calculate_check_digits(country: str, bban: str) -> str:
    temp_iban = bban + country + "00"
    numeric_str = ''.join(letter_to_number(c) for c in temp_iban)
    mod = 0
    for i in range(0, len(numeric_str), 7):
        chunk = numeric_str[i:i+7]
        mod = (mod * (10 ** len(chunk)) + int(chunk)) % 97
    check_digits = 98 - mod
    return f"{check_digits:02d}"

def generate_al():
    data = country_data["AL"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + account_number

def generate_ad():
    data = country_data["AD"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + account_number

def generate_at():
    data = country_data["AT"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + account_number

def generate_az():
    data = country_data["AZ"]
    bank_code = random.choice(data["bank_codes"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + account_number

def generate_bh():
    data = country_data["BH"]
    bank_code = random.choice(data["bank_codes"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + account_number

def generate_be():
    data = country_data["BE"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_numeric(data["account_length"])
    base = bank_code + account_number
    check_digits = f"{97 - (int(base) % 97):02d}"
    return bank_code + account_number + check_digits

def generate_ba():
    data = country_data["BA"]
    bank_code = generate_numeric(data["bank_code_length"])
    branch_code = generate_numeric(data["branch_code_length"])
    account_number = generate_numeric(data["account_length"])
    check_digits = generate_numeric(data["check_digits_length"])
    return bank_code + branch_code + account_number + check_digits

def generate_br():
    data = country_data["BR"]
    bank_code = generate_numeric(data["bank_code_length"])
    branch_code = generate_numeric(data["branch_code_length"])
    account_number = generate_numeric(data["account_length"])
    account_type = generate_alpha(data["account_type_length"])
    owner_type = generate_alpha(data["owner_type_length"])
    return bank_code + branch_code + account_number + account_type + owner_type

def generate_cr():
    data = country_data["CR"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + account_number

def generate_hr():
    data = country_data["HR"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + account_number

def generate_cy():
    data = country_data["CY"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + account_number

def generate_cz():
    data = country_data["CZ"]
    bank_code = generate_numeric(data["bank_code_length"])
    prefix = generate_numeric(data["prefix_length"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + prefix + account_number

def generate_dk():
    data = country_data["DK"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_numeric(data["account_length"])
    check_digit = generate_numeric(data["check_digit_length"])
    return bank_code + account_number + check_digit

def generate_do():
    data = country_data["DO"]
    bank_code = random.choice(data["bank_codes"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + account_number

def generate_eg():
    data = country_data["EG"]
    bank_code = generate_numeric(data["bank_code_length"])
    branch_code = generate_numeric(data["branch_code_length"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + branch_code + account_number

def generate_sv():
    data = country_data["SV"]
    bank_code = random.choice(data["bank_codes"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + account_number

def generate_ee():
    data = country_data["EE"]
    bank_code = generate_numeric(data["bank_code_length"])
    branch_code = generate_numeric(data["branch_code_length"])
    account_number = generate_numeric(data["account_length"])
    check_digit = generate_numeric(data["check_digit_length"])
    return bank_code + branch_code + account_number + check_digit

def generate_fo():
    data = country_data["FO"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_numeric(data["account_length"])
    check_digit = generate_numeric(data["check_digit_length"])
    return bank_code + account_number + check_digit

def generate_fi():
    data = country_data["FI"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_numeric(data["account_length"])
    check_digit = generate_numeric(data["check_digit_length"])
    return bank_code + account_number + check_digit

def generate_fr():
    data = country_data["FR"]
    bank_code = generate_numeric(data["bank_code_length"])
    branch_code = generate_numeric(data["branch_code_length"])
    account_number = generate_alphanum(data["account_length"])
    key = generate_numeric(data["key_length"])
    return bank_code + branch_code + account_number + key

def generate_ge():
    data = country_data["GE"]
    bank_code = random.choice(data["bank_codes"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + account_number

def generate_de():
    data = country_data["DE"]
    bank_code = random.choice(data["bank_codes"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + account_number

def generate_gi():
    data = country_data["GI"]
    bank_code = random.choice(data["bank_codes"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + account_number

def generate_gr():
    data = country_data["GR"]
    bank_code = generate_numeric(data["bank_code_length"])
    branch_code = generate_numeric(data["branch_code_length"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + branch_code + account_number

def generate_gl():
    data = country_data["GL"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_numeric(data["account_length"])
    check_digit = generate_numeric(data["check_digit_length"])
    return bank_code + account_number + check_digit

def generate_gt():
    data = country_data["GT"]
    bank_code = random.choice(data["bank_codes"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + account_number

def generate_hu():
    data = country_data["HU"]
    bank_code = generate_numeric(data["bank_code_length"])
    branch_code = generate_numeric(data["branch_code_length"])
    check_digit = generate_numeric(data["check_digit_length"])
    account_number = generate_numeric(data["account_length"])
    second_check_digit = generate_numeric(data["second_check_digit_length"])
    return bank_code + branch_code + check_digit + account_number + second_check_digit

def generate_is():
    data = country_data["IS"]
    bank_code = generate_numeric(data["bank_code_length"])
    branch_code = generate_numeric(data["branch_code_length"])
    identification = generate_numeric(data["identification_length"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + branch_code + identification + account_number

def generate_ie():
    data = country_data["IE"]
    bank_code = random.choice(data["bank_codes"])
    sort_code = generate_numeric(data["sort_code_length"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + sort_code + account_number

def generate_il():
    data = country_data["IL"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + account_number

def generate_it():
    data = country_data["IT"]
    bank_code = generate_numeric(data["bank_code_length"])
    branch_code = generate_numeric(data["branch_code_length"])
    account_number = generate_alphanum(data["account_length"])
    weights = [1, 0, 5, 7, 9, 13, 15, 17, 19, 21, 2, 4, 18, 20, 11, 3, 6, 8, 12, 14, 16, 10, 22, 25, 24, 23]
    cin_input = bank_code + branch_code + account_number
    total = sum((ord(c) - ord('0') if c.isdigit() else ord(c) - ord('A') + 10) * weights[i % 26] for i, c in enumerate(cin_input))
    cin = chr(65 + (total % 26))
    return cin + bank_code + branch_code + account_number

def generate_jo():
    data = country_data["JO"]
    bank_code = random.choice(data["bank_codes"])
    branch_code = generate_numeric(data["branch_code_length"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + branch_code + account_number

def generate_kz():
    data = country_data["KZ"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + account_number

def generate_xk():
    data = country_data["XK"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_numeric(data["account_length"])
    check_digits = generate_numeric(data["check_digits_length"])
    return bank_code + account_number + check_digits

def generate_kw():
    data = country_data["KW"]
    bank_code = random.choice(data["bank_codes"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + account_number

def generate_lv():
    data = country_data["LV"]
    bank_code = random.choice(data["bank_codes"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + account_number

def generate_lb():
    data = country_data["LB"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + account_number

def generate_li():
    data = country_data["LI"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + account_number

def generate_lt():
    data = country_data["LT"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + account_number

def generate_lu():
    data = country_data["LU"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + account_number

def generate_mk():
    data = country_data["MK"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_alphanum(data["account_length"])
    check_digits = generate_numeric(data["check_digits_length"])
    return bank_code + account_number + check_digits

def generate_mt():
    data = country_data["MT"]
    bank_code = random.choice(data["bank_codes"])
    branch_code = generate_numeric(data["branch_code_length"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + branch_code + account_number

def generate_mr():
    data = country_data["MR"]
    bank_code = generate_numeric(data["bank_code_length"])
    branch_code = generate_numeric(data["branch_code_length"])
    account_number = generate_numeric(data["account_length"])
    check_digits = generate_numeric(data["check_digits_length"])
    return bank_code + branch_code + account_number + check_digits

def generate_mc():
    data = country_data["MC"]
    bank_code = generate_numeric(data["bank_code_length"])
    branch_code = generate_numeric(data["branch_code_length"])
    account_number = generate_alphanum(data["account_length"])
    key = generate_numeric(data["key_length"])
    return bank_code + branch_code + account_number + key

def generate_me():
    data = country_data["ME"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_numeric(data["account_length"])
    check_digits = generate_numeric(data["check_digits_length"])
    return bank_code + account_number + check_digits

def generate_nl():
    data = country_data["NL"]
    bank_code = random.choice(data["bank_codes"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + account_number

def generate_no():
    data = country_data["NO"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_numeric(data["account_length"])
    check_digit = generate_numeric(data["check_digit_length"])
    return bank_code + account_number + check_digit

def generate_pk():
    data = country_data["PK"]
    bank_code = random.choice(data["bank_codes"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + account_number

def generate_pl():
    data = country_data["PL"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + account_number

def generate_pt():
    data = country_data["PT"]
    bank_code = generate_numeric(data["bank_code_length"])
    branch_code = generate_numeric(data["branch_code_length"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + branch_code + account_number

def generate_qa():
    data = country_data["QA"]
    bank_code = random.choice(data["bank_codes"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + account_number

def generate_md():
    data = country_data["MD"]
    bank_code = random.choice(data["bank_codes"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + account_number

def generate_ro():
    data = country_data["RO"]
    bank_code = random.choice(data["bank_codes"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + account_number

def generate_sm():
    data = country_data["SM"]
    bank_code = generate_numeric(data["bank_code_length"])
    branch_code = generate_numeric(data["branch_code_length"])
    account_number = generate_alphanum(data["account_length"])
    weights = [1, 0, 5, 7, 9, 13, 15, 17, 19, 21, 2, 4, 18, 20, 11, 3, 6, 8, 12, 14, 16, 10, 22, 25, 24, 23]
    cin_input = bank_code + branch_code + account_number
    total = sum((ord(c) - ord('0') if c.isdigit() else ord(c) - ord('A') + 10) * weights[i % 26] for i, c in enumerate(cin_input))
    cin = chr(65 + (total % 26))
    return cin + bank_code + branch_code + account_number

def generate_sa():
    data = country_data["SA"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + account_number

def generate_rs():
    data = country_data["RS"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_numeric(data["account_length"])
    check_digits = generate_numeric(data["check_digits_length"])
    return bank_code + account_number + check_digits

def generate_sk():
    data = country_data["SK"]
    bank_code = generate_numeric(data["bank_code_length"])
    prefix = generate_numeric(data["prefix_length"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + prefix + account_number

def generate_si():
    data = country_data["SI"]
    bank_code = generate_numeric(data["bank_code_length"])
    branch_code = generate_numeric(data["branch_code_length"])
    account_number = generate_numeric(data["account_length"])
    check_digits = generate_numeric(data["check_digits_length"])
    return bank_code + branch_code + account_number + check_digits

def generate_es():
    data = country_data["ES"]
    bank_code = generate_numeric(data["bank_code_length"])
    branch_code = generate_numeric(data["branch_code_length"])
    check_digits = generate_numeric(data["check_digits_length"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + branch_code + check_digits + account_number

def generate_se():
    data = country_data["SE"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_numeric(data["account_length"])
    check_digit = generate_numeric(data["check_digit_length"])
    return bank_code + account_number + check_digit

def generate_ch():
    data = country_data["CH"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + account_number

def generate_tl():
    data = country_data["TL"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_numeric(data["account_length"])
    check_digits = generate_numeric(data["check_digits_length"])
    return bank_code + account_number + check_digits

def generate_tr():
    data = country_data["TR"]
    bank_code = generate_numeric(data["bank_code_length"])
    reserved = generate_numeric(data["reserved_length"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + reserved + account_number

def generate_ua():
    data = country_data["UA"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_alphanum(data["account_length"])
    return bank_code + account_number

def generate_ae():
    data = country_data["AE"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + account_number

def generate_gb():
    data = country_data["GB"]
    bank_code = random.choice(data["bank_codes"])
    sort_code = generate_numeric(data["sort_code_length"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + sort_code + account_number

def generate_va():
    data = country_data["VA"]
    bank_code = generate_numeric(data["bank_code_length"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + account_number

def generate_vg():
    data = country_data["VG"]
    bank_code = random.choice(data["bank_codes"])
    account_number = generate_numeric(data["account_length"])
    return bank_code + account_number

COUNTRY_GENERATORS = {
    "AL": {"length": 28, "generator": generate_al},
    "AD": {"length": 24, "generator": generate_ad},
    "AT": {"length": 20, "generator": generate_at},
    "AZ": {"length": 28, "generator": generate_az},
    "BH": {"length": 22, "generator": generate_bh},
    "BE": {"length": 16, "generator": generate_be},
    "BA": {"length": 20, "generator": generate_ba},
    "BR": {"length": 29, "generator": generate_br},
    "CR": {"length": 22, "generator": generate_cr},
    "HR": {"length": 21, "generator": generate_hr},
    "CY": {"length": 28, "generator": generate_cy},
    "CZ": {"length": 24, "generator": generate_cz},
    "DK": {"length": 18, "generator": generate_dk},
    "DO": {"length": 28, "generator": generate_do},
    "EG": {"length": 29, "generator": generate_eg},
    "SV": {"length": 28, "generator": generate_sv},
    "EE": {"length": 20, "generator": generate_ee},
    "FO": {"length": 18, "generator": generate_fo},
    "FI": {"length": 18, "generator": generate_fi},
    "FR": {"length": 27, "generator": generate_fr},
    "GE": {"length": 22, "generator": generate_ge},
    "DE": {"length": 22, "generator": generate_de},
    "GI": {"length": 23, "generator": generate_gi},
    "GR": {"length": 27, "generator": generate_gr},
    "GL": {"length": 18, "generator": generate_gl},
    "GT": {"length": 28, "generator": generate_gt},
    "HU": {"length": 28, "generator": generate_hu},
    "IS": {"length": 26, "generator": generate_is},
    "IE": {"length": 22, "generator": generate_ie},
    "IL": {"length": 23, "generator": generate_il},
    "IT": {"length": 27, "generator": generate_it},
    "JO": {"length": 30, "generator": generate_jo},
    "KZ": {"length": 20, "generator": generate_kz},
    "XK": {"length": 20, "generator": generate_xk},
    "KW": {"length": 30, "generator": generate_kw},
    "LV": {"length": 21, "generator": generate_lv},
    "LB": {"length": 28, "generator": generate_lb},
    "LI": {"length": 21, "generator": generate_li},
    "LT": {"length": 20, "generator": generate_lt},
    "LU": {"length": 20, "generator": generate_lu},
    "MK": {"length": 19, "generator": generate_mk},
    "MT": {"length": 31, "generator": generate_mt},
    "MR": {"length": 27, "generator": generate_mr},
    "MC": {"length": 27, "generator": generate_mc},
    "ME": {"length": 22, "generator": generate_me},
    "NL": {"length": 18, "generator": generate_nl},
    "NO": {"length": 15, "generator": generate_no},
    "PK": {"length": 24, "generator": generate_pk},
    "PL": {"length": 28, "generator": generate_pl},
    "PT": {"length": 25, "generator": generate_pt},
    "QA": {"length": 29, "generator": generate_qa},
    "MD": {"length": 24, "generator": generate_md},
    "RO": {"length": 24, "generator": generate_ro},
    "SM": {"length": 27, "generator": generate_sm},
    "SA": {"length": 24, "generator": generate_sa},
    "RS": {"length": 22, "generator": generate_rs},
    "SK": {"length": 24, "generator": generate_sk},
    "SI": {"length": 19, "generator": generate_si},
    "ES": {"length": 24, "generator": generate_es},
    "SE": {"length": 24, "generator": generate_se},
    "CH": {"length": 21, "generator": generate_ch},
    "TL": {"length": 23, "generator": generate_tl},
    "TR": {"length": 26, "generator": generate_tr},
    "UA": {"length": 29, "generator": generate_ua},
    "AE": {"length": 23, "generator": generate_ae},
    "GB": {"length": 22, "generator": generate_gb},
    "VA": {"length": 22, "generator": generate_va},
    "VG": {"length": 24, "generator": generate_vg}
}

@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to the IBAN Generator API!",
        "description": "Generate valid IBANs for various countries with realistic bank details.",
        "tutorial": {
            "step1": "Send a GET request to /api/iban/gen with a country code parameter, e.g., /api/iban/gen?code=DE",
            "step2": "Receive a JSON response with the generated IBAN and detailed breakdown.",
            "step3": "Check supported countries at /api/iban/countries."
        },
        "example": {
            "endpoint": "/api/iban/gen?code=DE",
            "response": {
                "iban": "DE48370501981234567890",
                "country": "DE",
                "valid": True,
                "length": 22,
                "details": {
                    "bban": "370501981234567890",
                    "check_digits": "48",
                    "bank_code": "37050198",
                    "account_number": "1234567890"
                }
            }
        },
        "api_owner": "@ISmartCoder",
        "updates_channel": "t.me/TheSmartDev"
    })

@app.route("/api/iban/countries")
def list_countries():
    countries_list = [
        {"code": code, "name": pycountry.countries.get(alpha_2=code).name if pycountry.countries.get(alpha_2=code) else "Unknown"}
        for code in COUNTRY_GENERATORS.keys()
    ]
    return jsonify({
        "message": "Supported countries for IBAN generation",
        "total_countries": len(COUNTRY_GENERATORS),
        "countries": countries_list,
        "api_owner": "@ISmartCoder",
        "updates_channel": "t.me/TheSmartDev"
    })

@app.route("/api/iban/gen")
def generate_iban():
    country = request.args.get("code", "").upper()
    if country not in COUNTRY_GENERATORS:
        return jsonify({
            "error": "Unsupported country code",
            "message": "Please provide a valid country code. Check supported countries at /api/iban/countries.",
            "api_owner": "@ISmartCoder",
            "updates_channel": "t.me/TheSmartDev"
        }), 400
    bban = COUNTRY_GENERATORS[country]["generator"]()
    check_digits = calculate_check_digits(country, bban)
    iban = f"{country}{check_digits}{bban}"
    if len(iban) != COUNTRY_GENERATORS[country]["length"]:
        logger.error(f"Generated IBAN length mismatch for {country}: expected {COUNTRY_GENERATORS[country]['length']}, got {len(iban)}")
        return jsonify({
            "error": f"Generated IBAN length mismatch for {country}",
            "expected_length": COUNTRY_GENERATORS[country]["length"],
            "actual_length": len(iban),
            "api_owner": "@ISmartCoder",
            "updates_channel": "t.me/TheSmartDev"
        }), 500
    details = {"bban": bban, "check_digits": check_digits}
    data = country_data[country]
    offset = 0
    if "bank_codes" in data:
        details["bank_code"] = bban[:len(data["bank_codes"][0])]
        offset = len(data["bank_codes"][0])
    elif "bank_code_length" in data:
        details["bank_code"] = bban[:data["bank_code_length"]]
        offset = data["bank_code_length"]
    if "branch_code_length" in data:
        details["branch_code"] = bban[offset:offset+data["branch_code_length"]]
        offset += data["branch_code_length"]
    if "sort_code_length" in data:
        details["sort_code"] = bban[offset:offset+data["sort_code_length"]]
        offset += data["sort_code_length"]
    if "prefix_length" in data:
        details["prefix"] = bban[offset:offset+data["prefix_length"]]
        offset += data["prefix_length"]
    if "type_code_length" in data:
        details["type_code"] = bban[offset:offset+data["type_code_length"]]
        offset += data["type_code_length"]
    if "identification_length" in data:
        details["identification_number"] = bban[offset:offset+data["identification_length"]]
        offset += data["identification_length"]
    if "check_digits_length" in data:
        details["check_digits"] = bban[offset:offset+data["check_digits_length"]]
        offset += data["check_digits_length"]
    if "key_length" in data:
        details["key"] = bban[offset:offset+data["key_length"]]
        offset += data["key_length"]
    if "account_type_length" in data:
        details["account_type"] = bban[offset:offset+data["account_type_length"]]
        offset += data["account_type_length"]
    if "owner_type_length" in data:
        details["owner_type"] = bban[offset:offset+data["owner_type_length"]]
        offset += data["owner_type_length"]
    if "reserved_length" in data:
        details["reserved"] = bban[offset:offset+data["reserved_length"]]
        offset += data["reserved_length"]
    if "account_length" in data:
        details["account_number"] = bban[offset:offset+data["account_length"]]
    if "check_char" in data and data["check_char"]:
        details["cin"] = bban[0]
    return jsonify({
        "iban": iban,
        "country": country,
        "valid": True,
        "length": len(iban),
        "details": details,
        "api_owner": "@ISmartCoder",
        "updates_channel": "t.me/TheSmartDev"
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Sorry, You're Lost In Wrong Endpoint",
        "message": "Please use /api/iban/gen?code=<code> to generate an IBAN or /api/iban/countries to see supported countries.",
        "api_owner": "@ISmartCoder",
        "updates_channel": "t.me/TheSmartDev"
    }), 404

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
