import sys
from collections import defaultdict


def merge_results(files, output_file):
    all_results = []
    keys = [
        'logfile',
        'popsize',
        'keep_symptomatic',
        'prop_asym_carriers',
        'pre_quarantine',
        'interval',
        'n_simulation',
        'n_infection',
        'n_infection_failed',
        'n_infection_avoided',
        'n_infection_ignored',
        'n_show_symptom',
        'n_removal',
        'n_quarantine',
        'n_reintegration',
        'n_abort',
        'n_asym_infection',
        'n_presym_infection',
        'n_sym_infection',
        'n_remaining_popsize',
        'n_no_outbreak',
        'n_outbreak_duration',
        'n_no_infected_by_seed',
        'n_num_infected_by_seed',
        'n_first_infected_by_seed_on_day',
        'n_seed_show_no_symptom',
        'n_seed_show_symptom_on_day',
        'n_no_first_infection',
        'n_first_infection_on_day',
        'n_no_first_symptom',
        'n_first_symptom_on_day',
        'n_no_second_symptom',
        'n_second_symptom_on_day',
        'n_no_third_symptom',
        'n_third_symptom_on_day',
    ]
    all_keys = set()
    for file in files:
        result = defaultdict(int)
        with open(file) as input:
            for line in input:
                key, value = line.rstrip().split('\t')
                all_keys.add(key)
                result[key] = value
        all_results.append(result)
    # let us find all keys:
    available_keys = []
    for key in keys:
        if key in all_keys:
            available_keys.append(key)
        else:
            matching_keys = [x for x in all_keys if x.startswith(key)]
            matching_keys.sort(key=lambda x: int(x.rsplit('_', 1)[-1]))
            available_keys.extend(matching_keys)
    # now get available keys from all results
    for key in available_keys:
        sys.stdout.write(key)
        for res in all_results:
            sys.stdout.write('\t' + str(res[key]))
        sys.stdout.write('\n')


if __name__ == '__main__':
    input_files = sys.argv[1:]
    merge_results(input_files, 'merged_result.txt')