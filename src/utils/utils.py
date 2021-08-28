import re

def convert_compact_to_number(value: str) -> int:
    "This function converts compact string like (1.2k, 1m, 2B, 2) into number"

    if not value:
        return 0

    value = value.lower()

    # This will find out int or float from str
    seperated_number = re.findall(r"[-+]?\d*\.\d+|\d+", value)
    
    if not seperated_number:
        return 0
    
    def pure_int(s: str, multiply: int = 1)->int:
        return int(float(s) * multiply)

    seperated_number = seperated_number[0]
    if "k" in value:
        return pure_int(seperated_number, 1000)
    if "m" in value:
        return pure_int(seperated_number, 1000000)
    if "b" in value:
        return pure_int(seperated_number, 1000000000)
    if "t" in value:
        return pure_int(seperated_number, 1000000000000)
    return pure_int(seperated_number)

