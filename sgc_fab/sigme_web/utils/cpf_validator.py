""" This is a slight modification from the class created by author dudus
 (https://djangosnippets.org/users/dudus/) for use on the model layer.
 It is optimized for Python 3.5  and PEP8 compliant. """

import re

from django.core.validators import EMPTY_VALUES
from django.forms import ValidationError

__author__ = "Théo Carranza theocarranza@gmail.com"
__copyright__ = "Copyright (C) 2017 ThÃ©o Carranza"
__license__ = "Public Domain"
__version__ = "1.0"


ERROR_MESSAGES = {
    'invalid': "CPF inválido.",
    'digits_only': "Este campo requer somente números.",
    'max_digits': "Este campo requer exatamente 11 dígitos.",
}


def _dv_maker(remainder):
    if remainder >= 2:
        return 11 - remainder
    return 0


def calcular_dv(value):
    """
    Retorna o CPF com dígito verificador adicionado no final.

    Parâmetros:
    - value (str): 9 primeiros dígitos do CPF
    """

    # Precisamos somente dos 9 primeiros dígitos
    value = value[0:9]

    new_1dv = sum([i * int(value[idx])
                   for idx, i in enumerate(range(10, 1, -1))])
    new_1dv = _dv_maker(new_1dv % 11)
    value += str(new_1dv) + value[-1]
    new_2dv = sum([i * int(value[idx])
                   for idx, i in enumerate(range(11, 1, -1))])
    new_2dv = _dv_maker(new_2dv % 11)
    value = value[:-1] + str(new_2dv)

    return value


def validate_cpf(value):
    """
    Value can be either a string in the format XXX.XXX.XXX-XX or an
    11-digit number.
    """

    if value in EMPTY_VALUES:
        return ''
    if not value.isdigit():
        value = re.sub("[-.]", "", value)
    orig_value = value[:]

    # Elimina CPFs invalidos conhecidos
    if orig_value in ['00000000000', '11111111111', '22222222222',
                      '33333333333', '44444444444', '55555555555',
                      '66666666666', '77777777777', '88888888888',
                      '99999999999'
                      ]:
        raise ValidationError(ERROR_MESSAGES['invalid'])

    try:
        int(value)
    except ValueError:
        raise ValidationError(ERROR_MESSAGES['digits_only']) from ValueError
    if len(value) != 11:
        raise ValidationError(ERROR_MESSAGES['max_digits'])
    orig_dv = value[-2:]

    value = calcular_dv(value)

    if value[-2:] != orig_dv:
        raise ValidationError(ERROR_MESSAGES['invalid'])

    return orig_value
