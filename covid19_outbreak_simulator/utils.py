from fnmatch import fnmatch

def as_float(val, msg=''):
    try:
        return float(val)
    except Exception:
        raise ValueError(f'A float number is expected{" (" + msg + ")" if msg else ""}: {val} provided')


def as_int(val, msg=''):
    try:
        return int(val)
    except Exception:
        raise ValueError(f'An integer number is expected{" (" + msg + ")" if msg else ""}: {val} provided')

def parse_param_with_multiplier(args, subpops=None, default=None):
    if args is None:
        if default is not None:
            return {'': default}
        else:
            raise ValueError('Process multiplier of unspecified parameter')

    base = [x for x in args if not isinstance(x, str) or  '=' not in x]
    if not base:
        if default is None:
            raise ValueError(f'No vase value for multiplier: {" ".join(args)}')
        else:
            base = default
    else:
        try:
            base = [float(x) for x in base]
            if len(base) == 1:
                base = base[0]
        except:
            raise ValueError(f'Invalid parameter {" ".join(base)}')

    if not subpops:
        return {'': base}

    res = {x: base for x in subpops}
    for arg in [x for x in args if isinstance(x, str) and '=' in x]:
        sp, val = arg.split('=', 1)
        if sp.startswith('!'):
            sps = [x for x in subpops if not fnmatch(x, sp[1:])]
        elif sp in ('', 'all'):
            sps = ['']
        else:
            sps = [x for x in subpops if fnmatch(x, sp)]

        if not sps:
            raise ValueError(f'Invalid group name {sp}')
        try:
            val = float(val)
        except:
            raise ValueError(f'Invalid multiplier: {val}')
        #
        for sp in sps:
            if isinstance(base, (list, tuple)):
                res[sp] = [x * val for x in base]
            else:
                res[sp] = base * val
    return res