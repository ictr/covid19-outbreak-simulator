
def parse_param_with_multiplier(args, subpops=None, default=None):
    base = [x for x in args if '=' not in x]
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
    for arg in [x for x in args if '=' in x]:
        sp, val = arg.split('=', 1)
        if sp not in subpops:
            raise ValueError(f'Invalid subpopulation name {sp}')
        try:
            val = float(val)
        except:
            raise ValueError(f'Invalid multiplier: {val}')
        #
        if isinstance(base, (list, tuple)):
            res[sp] = [x * val for x in base]
        else:
            res[sp] = base * val

    return res