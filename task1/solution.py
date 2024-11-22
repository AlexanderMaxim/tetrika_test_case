from inspect import signature


def strict(func):
    def wrapper(*args, **kwargs):
        sig = signature(func)
        params = sig.parameters
        params_list = list(params.keys())

        for idx, arg in enumerate(args):
            param_name = params_list[idx]
            param_type = params[param_name].annotation
            if not isinstance(arg, param_type):
                raise TypeError(f'Аргумент "{param_name}" должен быть типа "{param_type}"')

        for key, val in kwargs.items():
            param_type = params[key].annotation
            if not isinstance(val, param_type):
                raise TypeError(f'Аргумент "{key}" должен быть типа "{param_type}"')

        result = func(*args, **kwargs)
        return result
    return wrapper


@strict
def sum_two(a: int, b: int) -> int:
    """
    Функция, возвращающая сумму двух целых чисел.

    Ключевые аргументы:
    :param a: первое целое число (int)
    :param b: второе целое число (int)
    """
    return a + b
