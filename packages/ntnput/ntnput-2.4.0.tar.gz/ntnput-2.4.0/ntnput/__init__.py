# +-------------------------------------+
# |         ~ Author : Xenely ~         |
# +=====================================+
# | GitHub: https://github.com/Xenely14 |
# | Discord: xenely                     |
# +-------------------------------------+

import time
import random
import typing
import ctypes
import contextlib

# Local imports
from . import misc

# ==-------------------------------------------------------------------== #
# Global and static variables, constants                                  #
# ==-------------------------------------------------------------------== #
LEFT_DOWN = 0x02
LEFT_UP = 0x04
RIGHT_DOWN = 0x10
RIGHT_UP = 0x08
MIDDLE_DOWN = 0x20
MIDDLE_UP = 0x40

KEY_DOWN = 0x00
KEY_UP = 0x02

# English layout keycodes
en_layout_keycodes = {
    "q": 0x51, "w": 0x57, "e": 0x45, "r": 0x52,
    "t": 0x54, "y": 0x59, "u": 0x55, "i": 0x49,
    "o": 0x4F, "p": 0x50, "a": 0x41, "s": 0x53,
    "d": 0x44, "f": 0x46, "g": 0x47, "h": 0x48,
    "j": 0x4A, "k": 0x4B, "l": 0x4C, "z": 0x5A,
    "x": 0x58, "c": 0x43, "v": 0x56, "b": 0x42,
    "n": 0x4E, "m": 0x4D

}

# Russian layout keycodes
ru_layout_keycodes = {
    "ё": 0xC0, "й": 0x51, "ц": 0x57, "у": 0x45,
    "к": 0x52, "е": 0x54, "н": 0x59, "г": 0x55,
    "ш": 0x49, "щ": 0x4F, "з": 0x50, "х": 0xDB,
    "ъ": 0xDD, "ф": 0x41, "ы": 0x53, "в": 0x44,
    "а": 0x46, "п": 0x47, "р": 0x48, "о": 0x4A,
    "л": 0x4B, "д": 0x4C, "ж": 0xBA, "э": 0xDE,
    "я": 0x5A, "ч": 0x58, "с": 0x43, "м": 0x56,
    "и": 0x42, "т": 0x4E, "ь": 0x4D, "б": 0xBC,
    "ю": 0xBE
}

# Special non-shifted characters keycodes
universal_chars_nonshift_keycodes = {
    "tab": 0x09, "alt": 0x12, "win": 0x5B, "end": 0x23,
    "esc": 0x1B, "home": 0x24, "ctrl": 0x11, "caps": 0x14,
    "space": 0x20, "pause": 0x13, "insert": 0x2D, "delete": 0x2E,
    "enter": 0x0D, "shift": 0x10, "print": 0x9A, "scroll": 0x91,
    "pageup": 0x21, "pagedown": 0x22,

    # Numlock keys
    "num0": 0x60, "num1": 0x61, "num2": 0x62, "num3": 0x63,
    "num4": 0x64, "num5": 0x65, "num6": 0x66, "num7": 0x67,
    "num8": 0x68, "num9": 0x69, "num*": 0x6A, "num+": 0x6B,
    "num-": 0x6D, "num.": 0x6E, "num/": 0x6F, "numlock": 0x90,

    # Functional keys
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73,
    "f5": 0x74, "f6": 0x75, "f7": 0x76, "f8": 0x77,
    "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,

    # Digits keys
    "0": 0x30, "1": 0x31, "2": 0x32, "3": 0x33,
    "4": 0x34, "5": 0x35, "6": 0x36, "7": 0x37,
    "8": 0x38, "9": 0x39,

    # Arrow keyc
    "left": 0x25, "up": 0x26, "right": 0x27, "down": 0x28,

    # Misc keys
    "-": 0xBD, "=": 0xBB, "\\": 0xDC, " ": 0x20,
}

# Special shifted english layout characters keycodes
en_chars_shifted_keycodes = {
    '"': 0xDE, "<": 0xBC, ">": 0xBE, "?": 0xBF,
    "{": 0xDB, "}": 0xDD, "~": 0xC0, ":": 0xBA,
    "|": 0xDC, "!": 0x31, "@": 0x32, "#": 0x33,
    "$": 0x34, "%": 0x35, "^": 0x36, "&": 0x37,
    "*": 0x38, "(": 0x39, ")": 0x30, "_": 0xBD,
    "+": 0xBB,
}

# Special non-shifted english layout characters keycodes
en_chars_nonshifted_keycodes = {
    "'": 0xDE, ",": 0xBC, ".": 0xBE, "/": 0xBF,
    "[": 0xDB, "]": 0xDD, "`": 0xC0, ";": 0xBA,
}

# Keycodes dict
keycodes = dict()

# Filling keycodes with letters
keycodes |= {key: {"code": value, "layout": "ru", "is_capital": False} for key, value in ru_layout_keycodes.items()}
keycodes |= {key: {"code": value, "layout": "en", "is_capital": False} for key, value in en_layout_keycodes.items()}

# Filling keycodes with upper letters
keycodes |= {key.upper(): value.copy() | {"is_capital": True} for key, value in keycodes.items() if len(key) == 1 and key.upper() != key}

# Saving letters dict
letters = keycodes.copy()

# Filling keycodes with special chars
keycodes |= {key: {"code": value, "layout": "en", "is_capital": True} for key, value in en_chars_shifted_keycodes.items()}
keycodes |= {key: {"code": value, "layout": "en", "is_capital": False} for key, value in en_chars_nonshifted_keycodes.items()}
keycodes |= {key: {"code": value, "layout": None, "is_capital": False} for key, value in universal_chars_nonshift_keycodes.items()}

# Mouse and keyboard delay
__mouse_delay = 0.05
__keyboard_delay = 0.05


# ==-------------------------------------------------------------------== #
# С-structures                                                            #
# ==-------------------------------------------------------------------== #
class InjectInputMouseInfo(ctypes.Structure):
    """Structure containing information about mouse input injection."""

    _fields_ = [
        ("x_direction", ctypes.c_int),
        ("y_direction", ctypes.c_int),
        ("mouse_data", ctypes.c_uint),
        ("mouse_options", ctypes.c_int),
        ("time_offset_in_miliseconds", ctypes.c_uint),
        ("extra_info", ctypes.c_void_p)
    ]


class KeybdInput(ctypes.Structure):
    """Structure containing information about keyboard input injection."""

    _fields_ = [
        ("vk_code", ctypes.c_ushort),
        ("scan_code", ctypes.c_ushort),
        ("dw_flags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("extra_info", ctypes.c_void_p)
    ]


# ==-------------------------------------------------------------------== #
# Wrapped syscall functions                                               #
# ==-------------------------------------------------------------------== #
_NtUserInjectMouseInput = misc.syscall("NtUserInjectMouseInput", result_type=ctypes.c_ulong, arguments_types=[ctypes.POINTER(InjectInputMouseInfo), ctypes.c_int], module=b"win32u.dll")
_NtUserInjectKeyboardInput = misc.syscall("NtUserInjectKeyboardInput", result_type=ctypes.c_ulong, arguments_types=[ctypes.POINTER(KeybdInput), ctypes.c_int], module=b"win32u.dll")


# ==-------------------------------------------------------------------== #
# Functions                                                               #
# ==-------------------------------------------------------------------== #
def __get_delay(delay: int | float | tuple[int | float, int | float]) -> int | float:
    """Gets delay depanding on passed value."""

    # Delay is defined value
    if isinstance(delay, (int, float)):
        return delay

    # Delay is random range
    if isinstance(delay, tuple) and len(delay) == 2 and isinstance(delay[0], (int, float)) and isinstance(delay[1], (int, float)):
        return random.uniform(*delay)

    raise Exception("Invalid delay value: `%s`, have to be type of: int | float | tuple[int | float, int | float]" % delay)


# ==-------------------------------------------------------------------== #
# Functions                                                               #
# ==-------------------------------------------------------------------== #
def get_default_mouse_delay() -> int | float:
    """Gets default mouse delay used when `delay` is `None` on mouse functions calls."""

    return __mouse_delay


def set_default_mouse_delay(delay: int | float | tuple[int | float, int | float]) -> None:
    """Sets default mouse delay used when `delay` is `None` on mouse functions calls."""

    global __mouse_delay

    try:
        # Validating delay
        __get_delay(delay)

        # Setting default mouse delay
        __mouse_delay = delay

    except Exception:
        raise


def get_default_keyboard_delay() -> int | float:
    """Gets default keyboard delay used when `delay` is `None` on keyboard functions calls."""

    return __keyboard_delay


def set_default_keyboard_delay(delay: int | float | tuple[int | float, int | float]) -> None:
    """Gets default keyboard delay used when `delay` is `None` on keyboard functions calls."""

    global __keyboard_delay

    try:
        # Validating delay
        __get_delay(delay)

        # Setting default mouse delay
        __keyboard_delay = delay

    except Exception:
        raise


def mouse_move(x: int, y: int, delay: int | float | tuple[int | float, int | float] = None) -> None:
    """Moves mouse relative to it's current position using wrapped syscall `NtUserInjectMouseInput` function."""

    # Moving mouse
    _NtUserInjectMouseInput(ctypes.byref(InjectInputMouseInfo(x_direction=x, y_direction=y)), 1)

    # Interval delay
    time.sleep(__get_delay(delay if delay is not None else __mouse_delay))


def mouse_move_to(x: int, y: int, delay: int | float | tuple[int | float, int | float] = None) -> None:
    """Moves mouse by absolute coorinate position using wrapped syscall `NtUserInjectMouseInput` function."""

    # Enable process DPI awareness to retrieve `indeed` screen resolution
    ctypes.windll.user32.SetProcessDPIAware()

    # Retrieving screen resolutions
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)

    # Normalizing coordinates
    normalized_x = int((x / screen_width) * 65_535)
    normalized_y = int((y / screen_height) * 65_535)

    # Moving mouse
    _NtUserInjectMouseInput(ctypes.byref(InjectInputMouseInfo(x_direction=normalized_x, y_direction=normalized_y, mouse_options=0x8000)), 1)

    # Interval delay
    time.sleep(__get_delay(delay if delay is not None else __mouse_delay))


def mouse_click(button: typing.Literal["left", "right", "middle"] = "left", delay: int | float | tuple[int | float, int | float] = None) -> None:
    """Clicks mouse using wrapped syscall `NtUserInjectMouseInput` function."""

    # If button literal is not allowed
    if button not in (allowed_literals := typing.get_args(mouse_click.__annotations__["button"])):
        raise Exception("Button literal is invalid, expected one of: `%s`" % ", ".join(allowed_literals))

    # Clicking mouse
    match button:

        case "left": _NtUserInjectMouseInput(ctypes.byref(InjectInputMouseInfo(mouse_options=LEFT_DOWN)), 1)
        case "right": _NtUserInjectMouseInput(ctypes.byref(InjectInputMouseInfo(mouse_options=RIGHT_DOWN)), 1)
        case "middle": _NtUserInjectMouseInput(ctypes.byref(InjectInputMouseInfo(mouse_options=MIDDLE_DOWN)), 1)

    # Interval delay
    time.sleep(__get_delay(delay if delay is not None else __mouse_delay))


def mouse_release(button: typing.Literal["left", "right", "middle"] = "left", delay: int | float | tuple[int | float, int | float] = None) -> None:
    """Releases mouse using wrapped syscall `NtUserInjectMouseInput` function."""

    # If button literal is not allowed
    if button not in (allowed_literals := typing.get_args(mouse_release.__annotations__["button"])):
        raise Exception("Button literal is invalid, expected one of: `%s`" % ", ".join(allowed_literals))

    # Releasing mouse
    match button:

        case "left": _NtUserInjectMouseInput(ctypes.byref(InjectInputMouseInfo(mouse_options=LEFT_UP)), 1)
        case "right": _NtUserInjectMouseInput(ctypes.byref(InjectInputMouseInfo(mouse_options=RIGHT_UP)), 1)
        case "middle": _NtUserInjectMouseInput(ctypes.byref(InjectInputMouseInfo(mouse_options=MIDDLE_UP)), 1)

    # Interval delay
    time.sleep(__get_delay(delay if delay is not None else __mouse_delay))


def mouse_click_and_release(button: typing.Literal["left", "right", "middle"] = "left", times: int = 1, delay: int | float | tuple[int | float, int | float] = None) -> None:
    """Clicks mouse and releases after given delay time passed in milliseconds using wrapped syscall `NtUserInjectMouseInput` function."""

    # If click times is invalid
    if times < 1:
        return

    # If button literal is not allowed
    if button not in (allowed_literals := typing.get_args(mouse_click_and_release.__annotations__["button"])):
        raise Exception("Button literal is invalid, expected one of: `%s`" % ", ".join(allowed_literals))

    # Clicking given times
    for _ in range(times):

        # Mouse clicking and releasing
        mouse_click(button, delay=__get_delay(delay if delay is not None else __mouse_delay)), mouse_release(button, delay=0)


def keyboard_press(key: str, delay: int | float | tuple[int | float, int | float] = None) -> None:
    """Presses keyboard key using wrapped syscall `NtUserInjectKeyboardInput` function."""

    # If key is not string
    if not isinstance(key, str):
        return

    # If key is invalid
    if (key_info := keycodes.get(key.lower())) is None:
        return

    # Pressing keyboard key
    _NtUserInjectKeyboardInput(ctypes.byref(KeybdInput(vk_code=key_info["code"], dw_flags=KEY_DOWN)), 1)

    # Interval delay
    time.sleep(__get_delay(delay if delay is not None else __keyboard_delay))


def keyboard_release(key: str, delay: int | float | tuple[int | float, int | float] = None) -> None:
    """Releases keyboard key using wrapped syscall `NtUserInjectKeyboardInput` function."""

    # If key is not string
    if not isinstance(key, str):
        return

    # If key is invalid
    if (key_info := keycodes.get(key.lower())) is None:
        return

    # Pressing keyboard key
    _NtUserInjectKeyboardInput(ctypes.byref(KeybdInput(vk_code=key_info["code"], dw_flags=KEY_UP)), 1)

    # Interval delay
    time.sleep(__get_delay(delay if delay is not None else __keyboard_delay))


def keyboard_press_and_release(key: str, delay: int | float | tuple[int | float, int | float] = None) -> None:
    """Presses keyboard key and releases after given delay time passed in milliseconds using wrapped syscall `NtUserInjectKeyboardInput` function."""

    # Keyboard pressing and releasing
    keyboard_press(key, delay=__get_delay(delay if delay is not None else __keyboard_delay)), keyboard_release(key, delay=0)


def keyboard_type(text: str, change_layout_delays: float = 0.05, delay: int | float | tuple[int | float, int | float] = None) -> None:
    """Types text using keyboard per-char keys press and releasing."""

    # Iterating every char and type it
    for key in text:

        # If key is invalid
        if (key_info := {key: value for key, value in keycodes.items() if len(key) == 1}.get(key)) is None:
            continue

        # Change keyboard layout if needed
        if (keyboard_layout := key_info.get("layout")) is not None:
            misc.change_keyboard_layout(keyboard_layout, delay=change_layout_delays)

        # Flags to chech if shift required
        caps_is_on = ctypes.windll.user32.GetKeyState(keycodes["caps"]["code"])
        shift_required = False

        # If key is letter
        if key in letters:
            shift_required = (key_info["is_capital"] and not caps_is_on & 0x0001 != 0) or (not key_info["is_capital"] and caps_is_on)

        else:
            shift_required = key in en_chars_shifted_keycodes

        # Press and release the key with Shift if needed
        with keyboard_hold("shift" if shift_required else None, delay=__get_delay(delay if delay is not None else __keyboard_delay)):
            keyboard_press_and_release(key, delay=__get_delay(delay if delay is not None else __keyboard_delay))


def keyboard_hotkey(*keys: str, delay: int | float | tuple[int | float, int | float] = None) -> None:
    """Press many keyboard keys and once."""

    # Hotkey activation
    with keyboard_hold(*keys, delay=__get_delay(delay if delay is not None else __keyboard_delay)):
        pass


@contextlib.contextmanager
def mouse_hold(*buttons: typing.Literal["left", "right", "middle"], delay: int | float | tuple[int | float, int | float] = None) -> typing.Generator[None, typing.Any, typing.Any]:
    """Hold mouse buttons until context manager exit."""

    # Button pressing
    for button in buttons:
        mouse_click(button, delay=__get_delay(delay if delay is not None else __mouse_delay))

    # Context exiting
    yield

    # Button releasing
    for button in buttons:
        keyboard_release(button, delay=__get_delay(delay if delay is not None else __mouse_delay))


@contextlib.contextmanager
def keyboard_hold(*keys: str, delay: int | float | tuple[int | float, int | float] = None) -> typing.Generator[None, typing.Any, typing.Any]:
    """Hold keyboard keys until context manager exit."""

    # Keys pressing
    for key in keys:
        keyboard_press(key, delay=__get_delay(delay if delay is not None else __keyboard_delay))

    # Context exiting
    yield

    # Keys releasing
    for key in keys:
        keyboard_release(key, delay=__get_delay(delay if delay is not None else __keyboard_delay))
