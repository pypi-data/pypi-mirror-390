# +-------------------------------------+
# |         ~ Author : Xenely ~         |
# +=====================================+
# | GitHub: https://github.com/Xenely14 |
# | Discord: xenely                     |
# +-------------------------------------+

import time
import ctypes
import struct
import typing
import ctypes.wintypes

# ==-------------------------------------------------------------------== #
# DLL functions                                                           #
# ==-------------------------------------------------------------------== #

# DLL libraries loading
_kernel32 = ctypes.windll.kernel32

# DLL libraries functions loading
_LoadLibraryA = _kernel32.LoadLibraryA
_GetProcAddress = _kernel32.GetProcAddress
_VirtualProtect = _kernel32.VirtualProtect

# Defining of DLL libraries functions return type
_LoadLibraryA.restype = ctypes.wintypes.LPVOID
_GetProcAddress.restype = ctypes.wintypes.LPVOID
_VirtualProtect.restype = ctypes.wintypes.BOOL

# Defining of DLL libraries functions argument types
_LoadLibraryA .argtypes = [ctypes.wintypes.LPCSTR]
_GetProcAddress.argtypes = [ctypes.wintypes.LPVOID, ctypes.wintypes.LPCSTR]
_VirtualProtect.argtypes = [ctypes.wintypes.LPVOID, ctypes.c_size_t, ctypes.wintypes.DWORD, ctypes.POINTER(ctypes.wintypes.DWORD)]


# ==-------------------------------------------------------------------== #
# Functions                                                               #
# ==-------------------------------------------------------------------== #
def syscall(nt_function_name: str, *, result_type: typing.Any, arguments_types: list[typing.Any], module: bytes = b"ntdll.dll") -> ctypes.WINFUNCTYPE:
    """Finds function in DLL module by it name, retrieves it's syscall ID, wraps it into raw function buffer and casts to `WINFUNCTYPE` to make call shadowed."""

    # Module loading
    if not (module_handle := _LoadLibraryA(module)):
        raise Exception("Unable to load module `%s`" % module.decode())

    # Retrieving nt-function pointer
    if not (nt_function := _GetProcAddress(module_handle, nt_function_name.encode())):
        raise Exception("Function `%s` not found" % nt_function_name)

    offset = 0
    syscall_id = None

    # Retrieving syscall ID from nt-function pointer
    while True:

        # Syscall ID not found
        if offset > 0x16:
            break

        # Retrieving syscall ID from memory
        if ctypes.cast(nt_function + offset, ctypes.POINTER(ctypes.c_ubyte)).contents.value == 0xB8:
            syscall_id = ctypes.cast(nt_function + offset + 1, ctypes.POINTER(ctypes.c_ushort)).contents.value
            break

        offset += 1

    # Syscall ID not found
    if syscall_id is None:
        raise Exception("Syscall ID for function `%s` not found" % nt_function_name)

    # Converting syscall ID to hex-bytes list
    syscall_id_bytes = [hex(item)[2:] if len(hex(item)[2:]) == 2 else "0" + hex(item)[2:] for item in struct.pack("<h", syscall_id)]

    # NOTE: I actually don't know why does this code require access `gs` segment.
    # I've just used this repo as reference: https://github.com/opcode86/SysCaller
    #
    # mov rax, gs:[0x60]
    # mov r10, rcx
    # mov eax, <syscall id>,
    # syscall
    # ret
    shellcode = bytes.fromhex("""
        65 48 8B 04 25 60 00
        00 00
        4C 8B D1
        B8 %s %s 00 00
        0F 05
        C3
    """ % tuple([*syscall_id_bytes]))

    # Allocating buffer for function machine code
    buffer = (ctypes.c_uint8 * len(shellcode))()
    shellcode_buffer = ctypes.cast(buffer, ctypes.c_void_p)

    # Copying shellcode into function machine code buffer
    ctypes.memmove(shellcode_buffer, ctypes.create_string_buffer(shellcode, len(shellcode)), len(shellcode))

    # Updating of function machine code buffer memory protection to make it executable
    ctypes.windll.kernel32.VirtualProtect(shellcode_buffer, len(shellcode), 0x40, ctypes.wintypes.LPDWORD(ctypes.wintypes.DWORD()))

    # Return wrapped syscall function
    return ctypes.cast(shellcode_buffer, ctypes.WINFUNCTYPE(result_type, *arguments_types))


def change_keyboard_layout(language_code_or_id: str | int, delay: int | float = 0.05) -> None:
    """Меняет языковую раскладку клавиатуры используя языковой ID."""

    # Словарь с кодами ID языков
    language_codes = {
        "en": 0x409,
        "ru": 0x419
    }

    # Если был передан код в качестве аргумента
    if isinstance(language_code_or_id, str):

        # Если код не найден
        if (language_code := language_codes.get(language_code_or_id.lower().strip())) is None:
            raise Exception("Unable to find code for `%s` language, use language ID instead" % language_code_or_id)

        # Установка ID языка
        language_code_or_id = language_code

    # Getting thread of active window
    current_thread = ctypes.windll.user32.GetWindowThreadProcessId(current_hwid := ctypes.windll.user32.GetForegroundWindow(), None)

    # If required language already set
    if ctypes.windll.user32.GetKeyboardLayout(current_thread) & 0xFFFF == language_code_or_id:
        return

    # Change keybord layout
    if not ctypes.windll.user32.PostMessageA(current_hwid, 0x50, 0, language_code_or_id):
        raise Exception("Unable to change keybord layout using `0x%s` code" % hex(language_code_or_id)[2:])

    # Change layout delay
    time.sleep(delay)
