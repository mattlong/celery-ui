from datetime import datetime


def parse_value(v):
    if isinstance(v, dict):
        if v['type'] == 'date':
            v = datetime.strptime(v['value'], '%Y/%m/%d').date()

        elif v['type'] == 'datetime':
            v = datetime.strptime(v['value'], '%Y/%m/%d %H:%M')

        elif v['type'] == 'float':
            v = float(v['value'])

    return v

def prepare_arguments(func, all_args):
    from inspect import getargspec
    positional, varargs, keywords, defaults = getargspec(func)

    args = []
    kwargs = {}

    if positional:
        if positional[0] == 'self':
            positional = positional[1:]

        for arg in positional:
            assert arg in all_args, 'positional argument "%s" not specified' % arg
            args.append(all_args[arg])
            del all_args[arg]

    if keywords:
        for arg in keywords.keys():
            assert arg in all_args, 'keyword argument "%s" not specified' % arg
            kwargs.append(all_args[arg])
            del all_args[arg]

    assert len(all_args.keys()) == 0, 'Extra arguments sent from interface: %s' % all_args
    return args, kwargs
