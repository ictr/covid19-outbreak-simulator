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
        'n_removal',
        'n_quarantine',
        'n_reintegration',
        'n_abort',
        'n_asym_infection',
        'n_sym_infection',
        'remaining_popsize_by_num',
        'no_outbreak',
        'outbreak_duration_by_day',
        'infection_from_seed_by_num',
        'no_infection_from_seed',
        'infection_from_seed_by_day',
        'no_symptom_from_seed',
        'symptom_from_seed_by_day',
        'no_first_infection',
        'first_infection_by_day',
        'no_first_symptom',
        'first_symptom_by_day',
        'no_second_symptom',
        'second_symptom_by_day',
        'no_third_symptom',
        'third_symptom_by_day',
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
            matching_keys = [x for x in all_keys if x.endswith(key)]
            matching_keys.sort(key=lambda x: int(x.split('_')[0]))
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