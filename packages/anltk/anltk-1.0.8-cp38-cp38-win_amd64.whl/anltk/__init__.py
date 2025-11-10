"""""" # start delvewheel patch
def _delvewheel_patch_1_10_0():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'anltk.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-anltk-1.0.8')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-anltk-1.0.8')) as file:
                load_order = file.read().split()
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.wintypes.HMODULE
            kernel32.LoadLibraryExW.argtypes = ctypes.wintypes.LPCWSTR, ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(lib_path, None, 8):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_10_0()
del _delvewheel_patch_1_10_0
# end delvewheel patch

from . import constants
from .version import __version__
from .anltk import \
    AR2BW, BW2AR, AR2SBW, SBW2AR, \
    TafqitOptions, \
    tafqit, \
    transliterate, \
    tokenize_words, \
    is_tashkeel, \
    is_arabic_alpha, \
    is_small, \
    is_indic_digit, \
    is_shamsi, \
    is_qamari, \
    remove_tashkeel, \
    remove_small, \
    remove_non_alpha, \
    remove_non_alpha_and_tashkeel, \
    remove_non_alphanumeric, \
    remove_non_alphanumeric_and_tashkeel, \
    remove_kasheeda, \
    normalize_hamzat, \
    duplicate_shadda_letter, \
    remove_if, \
    replace, \
    replace_str , \
    split, \
    fold_white_spaces ,\
    fold_if, \
    replace_if, \
    normalize_to_heh, \
    normalize_to_teh, \
    tokenize_if, \
    NoiseGenerator
