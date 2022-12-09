import string


def convert_base(
    num_s: str,
    target_base: int,
    current_base: int = 10,
    current_alphabet: str = "0123456789" + string.ascii_uppercase,
    target_alphabet: str = "0123456789" + string.ascii_uppercase,
) -> str:

    base_10 = 0
    digit = len(num_s) - 1
    for character in num_s:
        character_val = current_alphabet.index(character)
        base_10 += (current_base**digit) * character_val
        digit -= 1

    converted_num = ""
    floored_quotient = base_10
    while floored_quotient != 0:
        converted_num = target_alphabet[floored_quotient % target_base] + converted_num
        floored_quotient //= target_base

    if converted_num == "":
        converted_num = target_alphabet[0]

    return converted_num


def get_lexical_average(string1: str, string2: str) -> str:
    base10_string1 = int(convert_base(string1, 10, 26, string.ascii_lowercase))
    base10_string2 = int(convert_base(string2, 10, 26, string.ascii_lowercase))

    avg = (base10_string1 + base10_string2) // 2

    return convert_base(str(avg), 26, 10, target_alphabet=string.ascii_lowercase)


def get_lexical_rank(string1, string2):
    if string1.startswith("a") or string2.startswith("a"):
        raise Exception(f'Cannot get lexical rank for strings that begin with "a". Was given {string1} and {string2}.')

    max_len = max(len(string1), len(string2))

    while len(string1) < max_len:
        string1 += "a"

    while len(string2) < max_len:
        string2 += "a"

    lex_avg = get_lexical_average(string1, string2)

    if lex_avg == string1:
        lex_avg += "n"

    return lex_avg
