from .ansi_tools import ansi_supported as _ansi_supported
from .enums import HTMLColors, ANSIColors, StyleType, RGB, TextFormat
from .gv import RESET, ANSI


ansi_supported = _ansi_supported()


def _get_color_if_supported(color: str) -> str:
    if ansi_supported:
        return color
    return ''


def _fix_text(text: str) -> str:
    # i forget what i was gonna do here lol
    return text


def _convert_html_hex_to_ansi(text: str, color: HTMLColors | str, type: StyleType) -> str:
    if isinstance(color, str):
        # color is a HEX code
        if "#" in color:
            color = color.replace("#", "")
        color = color.lower().strip()
    else:
        # color is a HTMLColor enum, get the corresponding hex code
        color = color.value.lower().strip()

    color_chars = [char for char in color]

    rgb = RGB(
        int(color_chars[0] + color_chars[1], 16),
        int(color_chars[2] + color_chars[3], 16),
        int(color_chars[4] + color_chars[5], 16)
    )

    ansi_color = (
        (ANSI + ("38" if type == StyleType.FOREGROUND else "48") + ";2;[r];[g];[b]m")
        .replace("[r]", str(rgb.r))
        .replace("[g]", str(rgb.g))
        .replace("[b]", str(rgb.b))
    )

    return _get_color_if_supported(ansi_color) + _fix_text(text) + _get_color_if_supported(RESET)


def _get_ansi_color_code(text: str, color: ANSIColors, type: StyleType) -> str:
    return _get_color_if_supported(color.value) + _fix_text(text) + _get_color_if_supported(RESET)


def _get_ansi_color_code_with_formatting(text: str, color: ANSIColors, type: StyleType, formats: list[TextFormat] | None = None) -> str:
    color_code = _get_color_if_supported(color.value)
    format_codes = "".join([_get_color_if_supported(fmt.value) for fmt in formats]) if formats else ""
    reset_code = _get_color_if_supported(RESET)
    return color_code + format_codes + _fix_text(text) + reset_code


def _convert_html_hex_to_ansi_with_formatting(text: str, color: HTMLColors | str, type: StyleType, formats: list[TextFormat] | None = None) -> str:
    if not formats:
        return _convert_html_hex_to_ansi(text, color, type)

    colored_text = _convert_html_hex_to_ansi("", color, type)
    reset_code = _get_color_if_supported(RESET)

    if reset_code and colored_text.endswith(reset_code):
        color_code = colored_text[:-len(reset_code)]
    else:
        color_code = colored_text

    format_codes = "".join([_get_color_if_supported(fmt.value) for fmt in formats])
    return color_code + format_codes + _fix_text(text) + reset_code


def _apply_text_formatting(text: str, formats: list[TextFormat] | None = None) -> str:
    if not formats:
        return text

    format_codes = "".join([_get_color_if_supported(fmt.value) for fmt in formats])
    return format_codes + _fix_text(text) + _get_color_if_supported(RESET)
