import pytest
from itertools import product
from covid19_outbreak_simulator.simulator import Population



def test_population(population_factory):
    pop = population_factory(popsize=['100'])
    assert len(pop.individuals) == 100

    pop = population_factory(popsize=['A=100', 'B=200'])
    assert len(pop.individuals) == 300
    assert sorted(pop.group_sizes.keys()) == ['A', 'B']
    assert pop.group_sizes['A'] == 100
    assert pop.group_sizes['B'] == 200
    assert pop.max_ids['A'] == 100
    assert pop.max_ids['B'] == 200


def test_remove(population_factory):
    pop = population_factory(popsize=['100'])
    pop.remove('66')
    assert '66' not in pop.individuals
    assert pop.max_ids[''] == 100

    pop = population_factory(popsize=['A=100', 'B=200'])
    pop.remove('A_66')
    pop.remove('B_21')

    assert pop.group_sizes['A'] == 99
    assert pop.group_sizes['B'] == 199
    assert pop.max_ids['A'] == 100
    assert pop.max_ids['B'] == 200


def test_select(population_factory):
    # no vicinity
    pop = population_factory(popsize=['A=100', 'B=300'])
    cnt = {'A': 0, 'B': 0}
    for i in range(1000):
        selected = pop.select(infector='B_10')
        cnt[pop.individuals[selected].group] += 1

    assert cnt['A'] / (cnt['A'] + cnt['B']) > 0.15 and cnt['A'] / (cnt['A'] + cnt['B']) < 0.35
    assert cnt['B'] / (cnt['A'] + cnt['B']) > 0.60 and cnt['B'] / (cnt['A'] + cnt['B']) < 0.90

    cnt = {'A': 0, 'B': 0}
    for i in range(1000):
        selected = pop.select(infector='A_10')
        cnt[pop.individuals[selected].group] += 1

    assert cnt['A'] / (cnt['A'] + cnt['B']) > 0.15 and cnt['A'] / (cnt['A'] + cnt['B']) < 0.35
    assert cnt['B'] / (cnt['A'] + cnt['B']) > 0.60 and cnt['B'] / (cnt['A'] + cnt['B']) < 0.90

    # no within group infection
    pop = population_factory(popsize=['A=100', 'B=200'], vicinity=['A-A=0'])

    for i in range(10):
        selected = pop.select(infector='A_0')
        assert not selected.startswith('A')

    #
    pop = population_factory(popsize=['A=100', 'B=200'], vicinity=['A-A=50', 'A-B=10'])

    cnt = {'A': 0, 'B': 0}
    for i in range(1000):
        selected = pop.select(infector='A_0')
        cnt[pop.individuals[selected].group] += 1

    assert cnt['A'] / (cnt['A'] + cnt['B']) > 0.5 and cnt['A'] / (cnt['A'] + cnt['B']) < 0.95
    assert cnt['B'] / (cnt['A'] + cnt['B']) < 0.5 and cnt['B'] / (cnt['A'] + cnt['B']) > 0.05

    pop = population_factory(popsize=['A=100', 'B=300'], vicinity=['A-A=50', 'A-B=10'])
    cnt = {'A': 0, 'B': 0}
    for i in range(1000):
        selected = pop.select(infector='B_10')
        cnt[pop.individuals[selected].group] += 1

    assert cnt['A'] / (cnt['A'] + cnt['B']) > 0.15 and cnt['A'] / (cnt['A'] + cnt['B']) < 0.35
    assert cnt['B'] / (cnt['A'] + cnt['B']) > 0.60 and cnt['B'] / (cnt['A'] + cnt['B']) < 0.90

    # outside?
    pop = population_factory(popsize=['A=100', 'B=200'], vicinity=['A=0'])

    for i in range(10):
        selected = pop.select()
        assert not selected.startswith('A')

    #
    # ! match
    pop = population_factory(popsize=['A=100', 'B=200'], vicinity=['A=50', 'B=10', 'A-A=50', 'A-!A=10'])

    cnt = {'A': 0, 'B': 0}
    for i in range(1000):
        selected = pop.select(infector=None)
        cnt[pop.individuals[selected].group] += 1

    assert cnt['A'] / (cnt['A'] + cnt['B']) > 0.5 and cnt['A'] / (cnt['A'] + cnt['B']) < 0.95
    assert cnt['B'] / (cnt['A'] + cnt['B']) < 0.5 and cnt['B'] / (cnt['A'] + cnt['B']) > 0.05

    # wildcard
    pop = population_factory(popsize=['A=100', 'B=200'], vicinity=['A=50', 'B=10', 'A-*=50'])

    cnt = {'A': 0, 'B': 0}
    for i in range(1000):
        selected = pop.select(infector='A_10')
        cnt[pop.individuals[selected].group] += 1

    assert cnt['A'] / (cnt['A'] + cnt['B']) > 0.4 and cnt['A'] / (cnt['A'] + cnt['B']) < 0.6
    assert cnt['B'] / (cnt['A'] + cnt['B']) > 0.4 and cnt['B'] / (cnt['A'] + cnt['B']) < 0.6
