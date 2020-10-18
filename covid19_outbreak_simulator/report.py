import sys
import shlex
from collections import defaultdict


def summarize_simulations(logfile, output):
    if not output:
        return
    # write some summary information into standard output
    n_simulation = 0
    total_infection = 0
    total_infection_failed = 0
    total_infection_avoided = 0
    total_infection_ignored = 0
    total_show_symptom = 0
    total_removal = 0
    total_recover = 0
    total_quarantine = 0
    total_reintegration = 0
    total_abort = 0
    #
    total_asym_infection = 0
    total_presym_infection = 0
    total_sym_infection = 0
    #
    n_no_outbreak = 0
    n_remaining_popsize = defaultdict(int)
    n_outbreak_duration = defaultdict(int)
    #
    n_num_infected_by_seed = defaultdict(int)
    n_first_infected_by_seed_on_day = defaultdict(int)
    n_seed_show_symptom_on_day = defaultdict(int)
    n_first_symptom_on_day = defaultdict(int)
    n_first_infection_on_day = defaultdict(int)
    #
    n_second_symptom_on_day = defaultdict(int)
    n_third_symptom_on_day = defaultdict(int)
    #
    timed_stats = defaultdict(dict)
    customized_stats = defaultdict(dict)
    #
    if output == '-':
        outfile = sys.stdout
    else:
        outfile = open(output, 'w')
    with open(logfile) as lines:
        infection_from_seed_per_sim = defaultdict(int)
        infection_time_from_seed_per_sim = defaultdict(int)
        first_infection_day_per_sim = defaultdict(int)
        first_symptom_day_per_sim = defaultdict(int)
        second_symptom_per_sim = defaultdict(int)
        third_symptom_per_sim = defaultdict(int)

        total_popsize = 0
        infectors = []
        args = None

        for line in lines:
            try:
                id, time, event, target, params_field = line.split('\t')
            except:
                print(f'INVALID LOG LINE: {line}')
                continue
            if id == 'id':
                # skip header
                continue
            time = float(time)
            target = None if target == '.' else target
            params = params_field.split(',')
            #
            if event == 'START':
                from .cli import parse_args
                cmd_args = params_field.split(',args=')[-1]
                args = parse_args(shlex.split(cmd_args))
                if args.infectors:
                    infectors = args.infectors
                total_popsize = sum(int(x.split('=')[-1]) for x in args.popsize)
            elif event == 'INFECTION':
                total_infection += 1
                if any(x in params for x in [f'by={x}' for x in infectors]):
                    infection_from_seed_per_sim[id] += 1
                    if id not in infection_time_from_seed_per_sim:
                        infection_time_from_seed_per_sim[id] = time
                if time != 0 and id not in first_infection_day_per_sim:
                    first_infection_day_per_sim[id] = time
                for param in params:
                    if param.startswith('r_asym='):
                        total_asym_infection += int(param[7:])
                    elif param.startswith('r_presym='):
                        total_presym_infection += int(param[9:])
                    elif param.startswith('r_sym='):
                        total_sym_infection += int(param[6:])
            elif event == 'INFECTION_FAILED':
                total_infection_failed += 1
            elif event == 'INFECTION_AVOIDED':
                total_infection_avoided += 1
            elif event == 'INFECTION_IGNORED':
                total_infection_ignored += 1
            elif event == 'SHOW_SYMPTOM':
                total_show_symptom += 1
                if target in infectors:
                    n_seed_show_symptom_on_day[int(time) + 1] += 1
                elif id not in first_symptom_day_per_sim:
                    first_symptom_day_per_sim[id] = time
                elif id not in second_symptom_per_sim:
                    second_symptom_per_sim[
                        id] = time - first_symptom_day_per_sim[id]
                elif id not in third_symptom_per_sim:
                    third_symptom_per_sim[
                        id] = time - second_symptom_per_sim[id]
            elif event == 'REMOVAL':
                total_removal += 1
            elif event == 'QUARANTINE':
                total_quarantine += 1
            elif event == 'REINTEGRATION':
                total_reintegration += 1
            elif event == 'ABORT':
                total_abort += 1
            elif event == 'END':
                n_simulation += 1
                n_remaining_popsize[target] += 1
                n_outbreak_duration[0 if time == 0 else int(time) + 1] += 1
                if target == total_popsize and id not in first_symptom_day_per_sim:
                    n_no_outbreak += 1
            elif event == 'RECOVER':
                total_recover += 1
            elif event == 'STAT':
                id, time, event, target, params = line.split('\t')
                params = params.split(',')
                for param in params:
                    try:
                        key, value = param.split('=')
                        if time in timed_stats[key]:
                            timed_stats[key][
                                time] += ', ' + f'{id}:{value.strip()}'
                        else:
                            timed_stats[key][time] = f'{id}:{value.strip()}'
                    except Exception:
                        pass
            elif event == 'WARNING':
                pass
            elif event == 'ERROR':
                # an error has happened
                # params = line.split('\t')[-1]
                # err = eval(params.split('=', 1)[-1])
                sys.exit(f'Simulator exists with error')

            else:
                # customized events
                id, time, event, target, params = line.split('\t')
                params = params.split(',')
                for param in params:
                    try:
                        key, value = param.split('=')
                        if time in customized_stats[f'{event.lower()}_{key}']:
                            customized_stats[f'{event.lower()}_{key}'][
                                time] += ', ' + value.strip()
                        else:
                            customized_stats[f'{event.lower()}_{key}'][
                                time] = value.strip()
                    except Exception:
                        pass

    # summarize
    for v in infection_from_seed_per_sim.values():
        n_num_infected_by_seed[v] += 1
    #
    for v in infection_time_from_seed_per_sim.values():
        n_first_infected_by_seed_on_day[int(v) + 1] += 1
    n_first_infected_by_seed_on_day[0] = n_simulation - sum(
        n_first_infected_by_seed_on_day.values())
    #
    for v in first_infection_day_per_sim.values():
        n_first_infection_on_day[int(v) + 1] += 1
    n_first_infection_on_day[0] = n_simulation - sum(
        n_first_infection_on_day.values())
    #
    n_seed_show_symptom_on_day[0] = n_simulation - sum(
        n_seed_show_symptom_on_day.values())
    #
    for v in first_symptom_day_per_sim.values():
        n_first_symptom_on_day[int(v) + 1] += 1
    n_first_symptom = sum(n_first_symptom_on_day.values())
    #
    for v in second_symptom_per_sim.values():
        n_second_symptom_on_day[int(v) + 1] += 1
    n_second_symptom = sum(n_second_symptom_on_day.values())
    #
    for v in third_symptom_per_sim.values():
        n_third_symptom_on_day[int(v) + 1] += 1
    n_third_symptom = sum(n_third_symptom_on_day.values())
    #
    # print
    print(f'logfile\t{args.logfile}', file=outfile)
    print(f'popsize\t{" ".join(args.popsize)}', file=outfile)
    print(
        f'handle_symptomatic\t{" ".join(["remove", "1"] if args.handle_symptomatic is None else args.handle_symptomatic)}'
    , file=outfile)
    if args.symptomatic_r0:
        print(f'symptomatic_r0\t{" - ".join(args.symptomatic_r0)}', file=outfile)
    if args.asymptomatic_r0:
        print(f'asymptomatic_r0\t{" - ".join(args.asymptomatic_r0)}', file=outfile)
    if args.incubation_period:
        print(
            f'incubation_period\t{args.incubation_period[0]}({args.incubation_period[1]}, {args.incubation_period[2]}) '
            + ' '.join(args.incubation_period[3:]), file=outfile)
    if args.interval == 1 / 24:
        print(f'interval\t1 hour', file=outfile)
    elif args.interval == 1:
        print(f'interval\t1 day', file=outfile)
    else:
        print(f'interval\t{args.interval:.2f} day', file=outfile)
    if args.prop_asym_carriers:
        if len(args.prop_asym_carriers) == 1:
            print(
                f'prop_asym_carriers\t{float(args.prop_asym_carriers[0])*100:.1f}%', file=outfile
            )
        else:
            print(
                f'prop_asym_carriers\t{float(args.prop_asym_carriers[0])*100:.1f}% to {float(args.prop_asym_carriers[1])*100:.1f}%'
            , file=outfile)
    else:
        print(f'prop_asym_carriers\t10% to 40%', file=outfile)
    print(f'leadtime\t{"yes" if args.leadtime else "no"}', file=outfile)
    print(f'n_simulation\t{n_simulation}', file=outfile)
    print(f'total_infection\t{total_infection}', file=outfile)
    print(f'total_infection_failed\t{total_infection_failed}', file=outfile)
    print(f'total_infection_avoided\t{total_infection_avoided}', file=outfile)
    print(f'total_infection_ignored\t{total_infection_ignored}', file=outfile)
    print(f'total_show_symptom\t{total_show_symptom}', file=outfile)
    print(f'total_removal\t{total_removal}', file=outfile)
    print(f'total_recover\t{total_recover}', file=outfile)
    print(f'total_quarantine\t{total_quarantine}', file=outfile)
    print(f'total_reintegration\t{total_reintegration}', file=outfile)
    print(f'total_abort\t{total_abort}', file=outfile)
    print(f'total_asym_infection\t{total_asym_infection}', file=outfile)
    print(f'total_presym_infection\t{total_presym_infection}', file=outfile)
    print(f'total_sym_infection\t{total_sym_infection}', file=outfile)

    for num in sorted(n_remaining_popsize.keys()):
        print(f'n_remaining_popsize_{num}\t{n_remaining_popsize[num]}', file=outfile)
    # no outbreak is defined as final population size
    print(f'n_no_outbreak\t{n_no_outbreak}', file=outfile)
    for day in sorted(n_outbreak_duration.keys()):
        print(f'n_outbreak_duration_{day}\t{n_outbreak_duration[day]}', file=outfile)
    for num in sorted(n_num_infected_by_seed.keys()):
        print(f'n_num_infected_by_seed_{num}\t{n_num_infected_by_seed[num]}', file=outfile)
    for day in sorted(n_first_infected_by_seed_on_day.keys()):
        if day == 0:
            print(
                f'n_no_infected_by_seed\t{n_first_infected_by_seed_on_day[day]}'
            , file=outfile)
        else:
            print(
                f'n_first_infected_by_seed_on_day_{day}\t{n_first_infected_by_seed_on_day[day]}'
            , file=outfile)
    for day in sorted(n_seed_show_symptom_on_day.keys()):
        if day == 0:
            print(f'n_seed_show_no_symptom\t{n_seed_show_symptom_on_day[day]}', file=outfile)
        else:
            print(
                f'{day}_n_seed_show_symptom_on_day\t{n_seed_show_symptom_on_day[day]}'
            , file=outfile)
    for day in sorted(n_first_infection_on_day.keys()):
        if day == 0:
            print(f'n_no_first_infection\t{n_first_infection_on_day[day]}', file=outfile)
        else:
            print(
                f'n_first_infection_on_day_{day}\t{n_first_infection_on_day[day]}'
            , file=outfile)
    print(f'n_first_symptom\t{n_first_symptom}', file=outfile)
    for day in sorted(n_first_symptom_on_day.keys()):
        print(f'n_first_symptom_on_day_{day}\t{n_first_symptom_on_day[day]}', file=outfile)
    print(f'n_second_symptom\t{n_second_symptom}', file=outfile)
    for day in sorted(n_second_symptom_on_day.keys()):
        print(f'n_second_symptom_on_day_{day}\t{n_second_symptom_on_day[day]}', file=outfile)
    print(f'n_third_symptom\t{n_third_symptom}', file=outfile)
    for day in sorted(n_third_symptom_on_day.keys()):
        print(f'n_third_symptom_on_day_{day}\t{n_third_symptom_on_day[day]}', file=outfile)
    for item, timed_value in timed_stats.items():
        for time, value in timed_value.items():
            values = [x.strip() for x in value.split(',')]
            if len(set(values)) == 1 and len(values) > 1:
                value = f'[{values[0]}] * {len(values)}'
                print(f'{item}_{time}\t{value}', file=outfile)
            else:
                print(f'{item}_{time}\t{value.strip()}', file=outfile)
        for time, value in timed_value.items():
            try:
                value = eval('{' + value + '}')
                if len(value) > 1:
                    total = sum(value.values())
                    print(
                        f'avg_{item}_{time}\t{total/len(value):.5f}, {total/args.repeats:.5f}'
                    , file=outfile)
            except:
                pass
    for item, timed_value in customized_stats.items():
        for time, value in timed_value.items():
            values = [x.strip() for x in value.split(',')]
            if len(set(values)) == 1 and len(values) > 1:
                value = f'[{values[0]}] * {len(values)}'
                print(f'{item}_{time}\t{value}', file=outfile)
            else:
                print(f'{item}_{time}\t{value.strip()}', file=outfile)
        for time, value in timed_value.items():
            try:
                value = eval('{' + value + '}')
                if len(value) > 1:
                    total = sum(value.values())
                    print(
                        f'avg_{item}_{time}\t{total/len(value):.5f}, {total/args.repeats:.5f}'
                    , file=outfile)
            except:
                pass
    if output != '-':
        outfile.close()