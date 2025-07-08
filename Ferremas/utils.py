import re

def validar_rut(rut):
    return bool(re.match(r'^\d{7,8}-[\dkK]$', rut))