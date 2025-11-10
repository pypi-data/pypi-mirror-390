"""""" # start delvewheel patch
def _delvewheel_patch_1_11_2():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'anltk.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_2()
del _delvewheel_patch_1_11_2
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
