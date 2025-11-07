import re
import string
import unicodedata
from typing import Callable, List


class CharSet:
    alphabeta = set(string.ascii_letters)
    english_punctuations = set(".,;:?!\"'()[]{}<>-…~/|")
    chinese_punctuations = set("，。、；：？！“”‘’（）【】《》〈〉—……～")
    english_front_half_punctuations = set("([{<«‹「『")
    english_back_half_punctuations = set(")]}>»›」』")
    chinese_front_half_punctuations = set("（【《〈〔〖〘〚〝﹁﹃［｛｟")
    chinese_back_half_punctuations = set("）】》〉〕〗〙〛〞﹂﹄］｝｠")
    operators = set("+-*/%=!<>()[]{}|")
    digits_separators = set(".,")
    arabic_digits = set(string.digits)
    chinese_digits = set("零一二三四五六七八九十百千万亿")
    chinese_digits_upper = set("壹贰叁肆伍陆柒捌玖拾佰仟")
    spaces = set(
        [
            " ",
            "\xa0",  # 不间断空白符
            "\u0020",  # 半角
            "\u3000",  # 全角
            "\x20",  # UTF-8编码 普通空格字符
            "\u2003",  # unicode
            "\u00a0",
            "\x80",
            "\ufffd",
        ]
    )
    punctuations = (
        english_punctuations
        | chinese_punctuations
        | english_front_half_punctuations
        | english_back_half_punctuations
        | chinese_front_half_punctuations
        | chinese_back_half_punctuations
    )
    digits = arabic_digits | chinese_digits | chinese_digits_upper


char_set = CharSet()


def is_chinese(character):
    try:
        unicode_code = ord(character)
        return 0x4E00 <= unicode_code <= 0x9FFF
    except Exception:
        return False


def is_all_chinese(text: str):
    for char in text:
        if not is_chinese(char):
            return False
    return True


def is_all_arabic_digits(text):
    for char in text:
        if (
            char
            not in char_set.arabic_digits
            | char_set.operators
            | char_set.digits_separators
            | char_set.spaces
        ):
            return False
    return True


def chinese_punctuation_to_english(text):
    text = (
        text.replace("，", ",")
        .replace("。", ".")
        .replace("、", ",")
        .replace("；", ";")
        .replace("：", ":")
        .replace("？", "?")
        .replace("！", "!")
        .replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
        .replace("（", "(")
        .replace("）", ")")
        .replace("【", "[")
        .replace("】", "]")
        .replace("《", "<")
        .replace("》", ">")
        .replace("〈", "<")
        .replace("〉", ">")
        .replace("—", "-")
        .replace("……", "…")
        .replace("～", "~")
    )
    return text


def is_maths(text):
    for char in text:
        if (
            char
            not in char_set.arabic_digits
            | char_set.chinese_digits
            | char_set.chinese_digits_upper
            | char_set.operators
            | char_set.digits_separators
        ):
            return False
    return True


def has_digit(input_string):
    pattern = r"\d"  # 正则表达式，匹配任何数字字符
    if re.search(pattern, input_string):
        return True
    return False


def has_roman_numerals(input_string):
    clean_text = ""
    for c in input_string:
        if not is_chinese(c) and c.isalpha():  # 防止匹配到中文
            clean_text += c
    if clean_text:
        # 定义一个更精确的正则表达式模式，匹配罗马数字
        pattern = r"^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"

        if re.search(pattern, clean_text):
            return True
    return False


def _normalize_blanks(text: str, target: str):
    blank_pattern = r"[\s\xa0\x00\u0000\ue5e5\ue5ce\ufeff\u2003\u00a0\x80\ufffd]"
    normalized_text = re.sub(blank_pattern, target, text)
    normalized_text = re.sub(r"\s+", target, normalized_text)
    return normalized_text


def is_chinese_punctuation(character):
    try:
        # 中文标点符号的Unicode编码范围
        chinese_punctuation_range = (0x3000, 0x303F)
        # 获取字符的Unicode编码
        char_code = ord(character)

        # 判断字符是否在中文标点符号的Unicode编码范围内
        if chinese_punctuation_range[0] <= char_code <= chinese_punctuation_range[1]:
            return True
        else:
            if character in char_set.chinese_punctuations:
                return True
            else:
                return False
    except Exception:
        return False


def is_Qnumber(uchar):
    """判断一个unicode是否是全角数字"""
    if uchar >= "\uff10" and uchar <= "\uff19":
        return True
    else:
        return False


def is_Qalphabet(uchar):
    """判断一个unicode是否是全角英文字母"""
    if (uchar >= "\uff21" and uchar <= "\uff3a") or (
        uchar >= "\uff41" and uchar <= "\uff5a"
    ):
        return True
    else:
        return False


def Q2B(uchar):
    """单个字符 全角转半角"""
    inside_code = ord(uchar)
    if inside_code == 0x3000:
        inside_code = 0x0020
    else:
        inside_code -= 0xFEE0
    if inside_code < 0x0020 or inside_code > 0x7E:  # 转完之后不是半角字符返回原来的字符
        return uchar
    return chr(inside_code)


def stringQ2B(ustring: str, condition_fns: List[Callable] = []):
    """把字符串全角转半角"""
    if len(condition_fns) == 0:
        return "".join([Q2B(uchar) for uchar in ustring])

    norm_text = ""
    for char in ustring:
        if any([fn(char) for fn in condition_fns]):
            norm_text += Q2B(char)
        else:
            norm_text += char
    return norm_text


def stringpartQ2B(ustring):
    """把字符串中数字和字母全角转半角"""
    return stringQ2B(ustring, condition_fns=[is_Qnumber, is_Qalphabet])


def convert_to_simplified_chinese(text: str) -> str:
    import hanzidentifier
    from opencc import OpenCC

    text = unicodedata.normalize("NFKC", text)
    if hanzidentifier.identify(text) is hanzidentifier.TRADITIONAL:
        converter = OpenCC("t2s")
        text = converter.convert(text)
    return text


def normalize_char_text(
    char_text: str,
    Q2B_condition_fns: List[Callable] = [lambda x: not is_chinese_punctuation(x)],
) -> str:
    char_text = convert_to_simplified_chinese(char_text)
    char_text = _normalize_blanks(char_text, target=" ")
    char_text = stringQ2B(char_text, condition_fns=Q2B_condition_fns)
    return char_text.strip()


def remove_blanks(text: str):
    return _normalize_blanks(text, "")


def remove_english_punctuation(text: str):
    for p in char_set.english_punctuations:
        text = text.replace(p, "")
    return text


if __name__ == "__main__":
    text = """
     BCS PN Price/1000 pcs Unit Price 17013736-01 2,237.80 2.2378
    """
    print(normalize_char_text(text, Q2B_condition_fns=[]))

    def test_blank_characters():
        """Test and display all blank characters in the regex pattern"""

        # All the characters from the regex pattern
        blank_chars = [
            r"\s",  # This is a regex pattern, not a literal character
            "\xa0",  # Non-breaking space
            "\x00",  # Null character
            "\u0000",  # Null character (Unicode)
            "\ue5e5",  # Private use area
            "\ue5ce",  # Private use area
            "\ufeff",  # Zero width no-break space (BOM)
            "\u2003",  # Em space
            "\u00a0",  # Non-breaking space (same as \xa0)
            "\x80",  # Control character
            "\ufffd",  # Replacement character
        ]

        print("Testing blank characters from regex pattern:")
        print("=" * 60)

        for i, char in enumerate(blank_chars):
            if char == r"\s":
                print(f"{i + 1:2d}. {repr(char):<15} - Regex pattern for whitespace")
                continue

            # Get character info
            char_code = ord(char)
            char_name = char.encode("unicode_escape").decode("ascii")

            # Test if it's considered whitespace by Python
            is_whitespace = char.isspace()

            # Test if it's printable
            is_printable = char.isprintable()

            print(f"{i + 1:2d}. {repr(char):<15} - Code: {char_code:5d} ({char_name})")
            print(f"     Whitespace: {is_whitespace}, Printable: {is_printable}")

            # Show what it looks like in different contexts
            test_string = f"Hello{char}World"
            print(f"     In string: {repr(test_string)}")
            print()

        print("\n" + "=" * 60)
        print("Testing regex pattern:")

        import re

        pattern = r"[\s\xa0\x00\u0000\ue5e5\ue5ce\ufeff\u2003\u00a0\x80\ufffd]"
        print(f"Pattern: {pattern}")

        # Test with various strings
        test_strings = [
            "Hello World",
            "Hello\xa0World",
            "Hello\u2003World",
            "Hello\x00World",
            "Hello\ufeffWorld",
            "Hello\ue5e5World",
            "Hello\x80World",
            "Hello\ufffdWorld",
        ]

        for test_str in test_strings:
            result = re.sub(pattern, " ", test_str)
            print(f"'{test_str}' -> '{result}'")

    def show_unicode_info():
        """Show detailed Unicode information for each character"""

        chars_info = [
            ("\\s", "Regex whitespace pattern"),
            ("\\xa0", "Non-breaking space"),
            ("\\x00", "Null character"),
            ("\\u0000", "Null character (Unicode)"),
            ("\\ue5e5", "Private use area"),
            ("\\ue5ce", "Private use area"),
            ("\\ufeff", "Zero width no-break space (BOM)"),
            ("\\u2003", "Em space"),
            ("\\u00a0", "Non-breaking space"),
            ("\\x80", "Control character"),
            ("\\ufffd", "Replacement character"),
        ]

        print("\nDetailed Unicode Information:")
        print("=" * 60)

        for char_repr, description in chars_info:
            if char_repr == "\\s":
                print(f"{char_repr:<10} - {description}")
                continue

            # Convert string representation to actual character
            char = eval(f"'{char_repr}'")
            char_code = ord(char)

            print(f"{char_repr:<10} - {description}")
            print(f"           Unicode: U+{char_code:04X}")
            print(f"           Decimal: {char_code}")
            print(f"           Binary:  {bin(char_code)}")
            print(f"           Category: {char}")
            print()
