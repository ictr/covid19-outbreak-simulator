import copy
import random
from fnmatch import fnmatch


def as_float(val, msg=''):
    try:
        return float(val)
    except Exception as e:
        raise ValueError(
            f'A float number is expected{" (" + msg + ")" if msg else ""}: {val} provided'
        ) from e


def as_int(val, msg=''):
    try:
        return int(val)
    except Exception as e:
        raise ValueError(
            f'An integer number is expected{" (" + msg + ")" if msg else ""}: {val} provided'
        ) from e


def parse_param_with_multiplier(args, subpops=None, default=0, default_base=1):
    if args is None:
        if default is not None:
            return {'': default}
        else:
            raise ValueError('Process multiplier of unspecified parameter')

    base = [x for x in args if not isinstance(x, str) or '=' not in x]
    if not base:
        base = default_base
    else:
        try:
            base = [float(x) for x in base]
            if len(base) == 1:
                base = base[0]
        except Exception as e:
            raise ValueError(f'Invalid parameter {" ".join(base)}') from e

    if not subpops:
        return {'': default}

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
        except Exception as e:
            raise ValueError(f'Invalid multiplier: {val}') from e
        #
        for sp in sps:
            if isinstance(base, (list, tuple)):
                res[sp] = [x * val for x in base]
            else:
                res[sp] = base * val
    return res


def parse_target_param(status):
    if status is None:
        return lambda ind: True
    if isinstance(status, list):
        if len(status) == 1:
            return parse_target_param(status[0])
        else:
            raise ValueError('parse_target_param currently only support a single value.')

    if '&' in status:
        if status.count('&') > 1:
            raise ValueError(f'Currently only 1 & condition is allowed.')
        sts = status.split('&')
        return lambda ind: parse_target_param(sts[0])(ind) and parse_target_param(sts[1])(ind)
    if '|' in status:
        if status.count('|') > 1:
            raise ValueError(f'Currently only 1 & condition is allowed.')
        sts = status.split('|')
        return lambda ind: parse_target_param(sts[0])(ind) or parse_target_param(sts[1])(ind)
    if status.startswith('!'):
        return lambda ind: not parse_target_param(status[1:])(ind)

    if status == 'infected':
        return lambda ind: isinstance(ind.infected, float) and not isinstance(
            ind.recovered, float)
    elif status == 'uninfected':
        return lambda ind: not isinstance(ind.infected, float)
    elif status == 'recovered':
        return lambda ind: isinstance(ind.recovered, float)
    elif status == 'quarantined':
        return lambda ind: isinstance(ind.quarantined, float)
    elif status == 'unquarantined':
        return lambda ind: not isinstance(ind.quarantined, float)
    elif status == 'vaccinated':
        return lambda ind: isinstance(ind.vaccinated, float)
    elif status == 'unvaccinated':
        return lambda ind: not isinstance(ind.vaccinated, float)
    elif status == 'all':
        return lambda ind: True
    else:
        raise ValueError(f'Unexpected conditions {status}')


def select_individuals(population, IDs, targets, max_count=None):
    from_IDs = copy.deepcopy(IDs)
    random.shuffle(from_IDs)

    def add_ind(match_cond, limit=None):
        nonlocal from_IDs
        res = []
        count = 0
        for ID in from_IDs:
            if match_cond(population[ID]):
                res.append(ID)
                count += 1
                if limit is not None and count == limit:
                    break
        from_IDs = list(set(from_IDs) - set(res))
        return res

    selected = []
    for target in targets or ['all']:
        is_target = parse_target_param(target)
        selected.extend(
            add_ind(
                is_target,
                None if max_count is None else max_count - len(selected)))
        if max_count is not None and len(selected) == max_count:
            break
    return selected


def parse_handle_symptomatic_options(handle_symptomatic_arg, group):
    hs_args = None
    for hs in handle_symptomatic_arg or []:
        # multiplier
        if '=' in hs.split('?', 1)[0]:
            if hs.startswith(group + '='):
                hs_args = hs[len(group) + 1:]
                break
        else:
            hs_args = hs

    if not hs_args:
        handle_symptomatic = {'reaction': "remove", 'proportion': 1, "tracing": None}
    else:
        handle_symptomatic = {'reaction': hs_args.split('?')[0], "tracing": None}
        if '?' in hs_args:
            for option in hs_args.split('?')[1].split('&'):
                if '=' not in option:
                    raise ValueError(f'Wrong option {hs_args}')
                k, v = option.split('=', 1)
                if k not in ('proportion', 'duration', 'infected', 'tracing'):
                    raise ValueError(
                        f'Unrecognized option {k} in option {hs_args}')

                if k in ('proportion', 'duration', 'tracing'):
                    try:
                        handle_symptomatic[k] = float(v)
                    except Exception as e:
                        raise ValueError(
                            f"Option {k} in --handle-symptomatic should be a float number, {v} specified"
                        ) from e
                    if k == 'proportion' and (handle_symptomatic[k] > 1 or
                                            handle_symptomatic[k] < 0):
                        raise ValueError(
                            f'Proportion in "--handle-symptomatic remove/keep prop" should be a float number between 0 and 1: {handle_symptomatic[k]} provided'
                        )
                elif k == 'infected':
                    if v.lower() == 'true':
                        handle_symptomatic[k] = True
                    elif v.lower() == 'false':
                        handle_symptomatic[k] = False
                    else:
                        raise ValueError(f'Parameter infected can only be True or False. {v} specified')
        else:
            handle_symptomatic['proportion'] = 1

    return handle_symptomatic
