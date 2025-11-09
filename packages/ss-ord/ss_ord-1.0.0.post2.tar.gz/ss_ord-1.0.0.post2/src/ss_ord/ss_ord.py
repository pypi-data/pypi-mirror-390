def SS1_code(string, shift=10):
    # Args:
    # string - String to code
    # shift - Shift

    result = ""

    for c in string:
        alpha_result = ord(c)
        beta_result = alpha_result + shift
        final_char = chr(beta_result)
        result += final_char

    return result

def SS1_decode(string, shift=10):
    # Args:
    # string - String to decode
    # shift - Shift

    result = ""

    for c in string:
        alpha_result = ord(c)
        beta_result = alpha_result - shift
        final_char = chr(beta_result)
        result += final_char

    return result
