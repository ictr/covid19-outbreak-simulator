=====
Usage
=====


This simulator is programmed using Python >= 3.6 with ``numpy`` and ``scipy``.
A conda environment is recommended. After the set up of the environment,
please run

.. code-block:: sh

   pip install -r requirements.txt

to install required packages, and then

.. code-block:: sh

   pip install covid19-outbreak-simulator

to install the package.

You can then use command

.. code-block:: sh

   outbreak_simulator -h

to check the usage information.

Command line options
--------------------

.. code-block:: sh

   $ outbreak_simulator -h
   usage: outbreak_simulator [-h] [--popsize POPSIZE [POPSIZE ...]]
                          [--susceptibility SUSCEPTIBILITY [SUSCEPTIBILITY ...]]
                          [--symptomatic-r0 SYMPTOMATIC_R0 [SYMPTOMATIC_R0 ...]]
                          [--asymptomatic-r0 ASYMPTOMATIC_R0 [ASYMPTOMATIC_R0 ...]]
                          [--incubation-period INCUBATION_PERIOD [INCUBATION_PERIOD ...]]
                          [--repeats REPEATS] [--keep-symptomatic]
                          [--pre-quarantine [PRE_QUARANTINE [PRE_QUARANTINE ...]]]
                          [--infectors [INFECTORS [INFECTORS ...]]]
                          [--interval INTERVAL] [--logfile LOGFILE]
                          [--prop-asym-carriers [PROP_ASYM_CARRIERS [PROP_ASYM_CARRIERS ...]]]
                          [--allow-lead-time] [--analyze-existing-logfile]
                          [-j JOBS]

   optional arguments:
     -h, --help            show this help message and exit
     --popsize POPSIZE [POPSIZE ...]
                           Size of the population, including the infector that
                           will be introduced at the beginning of the simulation.
                           It should be specified as a single number, or a serial
                           of name=size values for different groups. For example
                           "--popsize nurse=10 patient=100". The names will be
                           used for setting group specific parameters. The IDs of
                           these individuals will be nurse0, nurse1 etc.
     --susceptibility SUSCEPTIBILITY [SUSCEPTIBILITY ...]
                           Weight of susceptibility. The default value is 1,
                           meaning everyone is equally susceptible. With options
                           such as "--susceptibility nurse=1.2 patients=0.8" you
                           can give weights to different groups of people so that
                           they have higher or lower probabilities to be
                           infected.
     --symptomatic-r0 SYMPTOMATIC_R0 [SYMPTOMATIC_R0 ...]
                           Production number of symptomatic infectors, should be
                           specified as a single fixed number, or a range, and/or
                           multipliers for different groups such as A=1.2. For
                           example "--symptomatic-r0 1.4 2.8 nurse=1.2" means a
                           general R0 ranging from 1.4 to 2.8, while nursed has a
                           range from 1.4*1.2 and 2.8*1.2.
     --asymptomatic-r0 ASYMPTOMATIC_R0 [ASYMPTOMATIC_R0 ...]
                           Production number of asymptomatic infectors, should be
                           specified as a single fixed number, or a range and/or
                           multipliers for different groups
     --incubation-period INCUBATION_PERIOD [INCUBATION_PERIOD ...]
                           Incubation period period, should be specified as
                           "lognormal" followed by two numbers as mean and sigma,
                           or "normal" followed by mean and sd, and/or
                           multipliers for different groups. Default to
                           "lognormal 1.621 0.418"
     --repeats REPEATS     Number of replicates to simulate. An ID starting from
                           1 will be assinged to each replicate and as the first
                           columns in the log file.
     --keep-symptomatic    Keep affected individuals in the population
     --pre-quarantine [PRE_QUARANTINE [PRE_QUARANTINE ...]]
                           Days of self-quarantine before introducing infector to
                           the group. The simulation will be aborted if the
                           infector shows symptom before introduction. If you
                           quarantine multiple people or specified named groups,
                           you will need to append the IDs to the parameter (e.g.
                           --pre-quarantine day nurse1 nurse2
     --infectors [INFECTORS [INFECTORS ...]]
                           Infectees to introduce to the population, default to
                           '0'. If you would like to introduce multiple infectees
                           to the population, or if you have named groups, you
                           will have to specify the IDs of carrier such as
                           --infectors nurse1 nurse2
     --interval INTERVAL   Interval of simulation, default to 1/24, by hour
     --logfile LOGFILE     logfile
     --prop-asym-carriers [PROP_ASYM_CARRIERS [PROP_ASYM_CARRIERS ...]]
                           Proportion of asymptomatic cases. You can specify a
                           fix number, or two numbers as the lower and higher CI
                           (95%) of the proportion. Default to 0.10 to 0.40.
     --allow-lead-time     The seed carrier will be asumptomatic but always be at
                           the beginning of incurbation time. If allow lead time
                           is set to True, the carrier will be anywhere in his or
                           her incubation period.
     --analyze-existing-logfile
                           Analyze an existing logfile, useful for updating the
                           summarization procedure or uncaptured output.
     -j JOBS, --jobs JOBS  Number of process to use for simulation. Default to
                           number of CPU cores.

Homogeneous and heterogeneous populations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: sh

   outbreak_simulator

simulates the outbreak of COVID-19 in a population with 64 individuals, with one
introduced infector.

.. code-block:: sh

   outbreak_simulator --popsize nurse=10 patient=100 --infector patient0

simulates a population with ``10`` nurses and ``100`` patients when the first patient
carries the virus.

Change number of infectors
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: sh

   outbreak_simulator --infector 0 1 --pre-quarantine 7 0 1

simulates the introduction of two infectors, both after 7 days of quarantine. Here
``0`` and ``1`` are IDs of individuals

Changing model parameters
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: sh

   outbreak_simulator --prop-asym-carriers 0.10

runs the simulation with a fixed ratio of asymptomatic carriers.

.. code-block:: sh

   outbreak_simulator --incubation-period normal 4 2

runs the simulation incubation period sampled from a normal distribution with
mean 4 and standard deviation of 2.

Specigy group-specific parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Parameters ``symptomatic-r0``\ , ``asymptomatic-r0`` and ``incubation-period`` can be
set to different values for each groups. These are achived by "multipliers",
which multiplies specified values to values drawn from the default distribution.

For example, if in a hospital environment nurses, once affected, tends to have
higher ``R0`` because he or she contact more patients, and on the other hand
patients are less mobile and should have lower ``R0``. In some cases the nurses
are even less protected and are more susceptible. You can run a simulation
with two patients carrying the virus with the following options:

.. code-block:: sh

   outbreak_simulator --popsize nurse=10 patient=100 \
       --symptomatic-r0 nurse=1.5 patient=0.8 \
       --asymptomatic-r0 nurse=1.5 patient=0.8 \
       --susceptibility nurse=1.2 patient=0.8 \
       --infector patient0 patient1

Output from the simulator
-------------------------

The output file contains events that happens during the simulations.
For example, for command

.. code-block:: sh

   outbreak_simulator --repeat 100 --popsize 64 --logfile result_remove_symptomatic.txt

You will get an output file ``result_remove_symptomatic.txt`` with the following columns:

.. list-table::
   :header-rows: 1

   * - column
     - content
   * - ``id``
     - id of the simulation.
   * - ``time``
     - time of the event in days, accurate to hour.
   * - ``event``
     - type of event
   * - ``target``
     - subject of the event, for example the ID of the individual that has been quarantined.
   * - ``params``
     - Additional parameters, mostly for the ``INFECTION`` event where simulated $R_0$ and incubation period will be displayed.


Currently the following events are tracked

.. list-table::
   :header-rows: 1

   * - Name
     - Event
   * - ``INFECTION``
     - Infect an non-quarantined individual, who might already been infected.
   * - ``INFECION_FAILED``
     - No one left to infect
   * - ``INFECTION_AVOIDED``
     - An infection happended during quarantine. The individual might not have showed sympton.
   * - ``INFECTION_IGNORED``
     - Infect an infected individual, which does not change anything.
   * - ``SHOW_SYMPTOM``
     - Show symptom.
   * - ``REMOVAL``
     - Remove from population.
   * - ``QUANTINE``
     - Quarantine someone till specified time.
   * - ``REINTEGRATION``
     - Reintroduce the quarantined individual to group.
   * - ``ABORT``
     - If the first carrier show sympton during quarantine.
   * - ``END``
     - Simulation ends.


The log file of a typical simulation would look like the following:

.. code-block:: sh

   id      time    event   target  params
   5       0.00    INFECTION       0       r0=0.53,r=0,r_asym=0
   5       0.00    END     64      popsize=64,prop_asym=0.276
   2       0.00    INFECTION       0       r0=2.42,r=1,r_presym=1,r_sym=0,incu=5.51
   2       4.10    INFECTION       62      by=0,r0=1.60,r=2,r_presym=2,r_sym=0,incu=5.84
   2       5.51    SHOW_SYMPTOM    0       .
   2       5.51    REMOVAL 0       popsize=63
   2       9.59    INFECTION       9       by=62,r0=2.13,r=2,r_presym=2,r_sym=0,incu=3.34
   2       9.84    INFECTION_IGNORED       9       by=62
   2       9.94    SHOW_SYMPTOM    62      .
   2       9.94    REMOVAL 62      popsize=62
   2       10.76   INFECTION       30      by=9,r0=1.96,r=2,r_presym=2,r_sym=0,incu=4.85
   2       11.64   INFECTION       57      by=9,r0=0.39,r=0,r_asym=0
   2       12.23   INFECTION       56      by=30,r0=1.65,r=1,r_presym=1,r_sym=0,incu=4.26
   2       12.93   SHOW_SYMPTOM    9       .
   2       12.93   REMOVAL 9       popsize=61
   2       14.37   INFECTION       6       by=30,r0=1.60,r=0,r_presym=0,r_sym=0,incu=2.63
   2       15.61   SHOW_SYMPTOM    30      .
   2       15.61   REMOVAL 30      popsize=60
   2       16.37   INFECTION       1       by=56,r0=1.57,r=1,r_presym=1,r_sym=0,incu=5.14
   2       16.49   SHOW_SYMPTOM    56      .
   2       16.49   REMOVAL 56      popsize=59
   2       16.99   SHOW_SYMPTOM    6       .
   2       16.99   REMOVAL 6       popsize=58
   2       18.42   INFECTION       8       by=1,r0=2.45,r=1,r_presym=1,r_sym=0,incu=3.74
   2       20.35   INFECTION       44      by=8,r0=2.37,r=1,r_presym=1,r_sym=0,incu=3.92
   2       21.51   SHOW_SYMPTOM    1       .
   2       21.51   REMOVAL 1       popsize=57
   2       22.16   SHOW_SYMPTOM    8       .
   2       22.16   REMOVAL 8       popsize=56
   2       22.62   INFECTION       42      by=44,r0=1.49,r=0,r_presym=0,r_sym=0,incu=4.30
   2       24.27   SHOW_SYMPTOM    44      .
   2       24.27   REMOVAL 44      popsize=55
   2       26.92   SHOW_SYMPTOM    42      .
   2       26.92   REMOVAL 42      popsize=54
   2       26.92   END     54      popsize=54,prop_asym=0.216
   1       0.00    INFECTION       0       r0=2.00,r=2,r_presym=2,r_sym=0,incu=4.19

which I assume would be pretty self-explanatory. Note that **the simulation IDs
are not ordered because the they are run in parallel but you can expect all events
belong to the same simulation are recorded together.**.

Summary report from multiple replicates
---------------------------------------

At the end of each command, a report will be given to summarize key statistics from
multiple replicated simulations. The output contains the following keys and their values

.. list-table::
   :header-rows: 1

   * - name
     - value
   * - ``logfile``
     - Log file of the simulation with all the events
   * - ``popsize``
     - Initial population size
   * - ``keep_symptomatic``
     - If asymptomatic infectees are kept
   * - ``prop_asym_carriers``
     - Proportion of asymptomatic carriers, also the probability of infectee who do not show any symptom
   * - ``pre_quarantine``
     - If the first carrier is pre-quarantined, if so, for how many days
   * - ``interval``
     - Interval of time events (1/24 for hours)
   * - ``n_simulation``
     - Total number of simulations, which is the number of ``END`` events
   * - ``total_infection``
     - Number of ``INFECTION`` events
   * - ``total_infection_failed``
     - Number of ``INFECTION_FAILED`` events
   * - ``total_infection_avoided``
     - Number of ``INFECTION_AVOIDED`` events
   * - ``total_infection_ignored``
     - Number of ``INFECTION_IGNORED`` events
   * - ``total_show_symptom``
     - Number of ``SHOW_SYMPTOM`` events
   * - ``total_removal``
     - Number of ``REMOVAL`` events
   * - ``total_quarantine``
     - Number of ``QUARANTINE`` events
   * - ``total_reintegration``
     - Number of ``REINTEGRATION`` events
   * - ``total_abort``
     - Number of ``ABORT`` events
   * - ``total_asym_infection``
     - Number of asymptomatic infections
   * - ``total_presym_infection``
     - Number of presymptomatic infections
   * - ``total_sym_infection``
     - Number of symptomatic infections
   * - ``n_remaining_popsize_XXX``
     - Number of simulations with ``XXX`` remaining population size
   * - ``n_no_outbreak``
     - Number of simulations with no outbreak (no symptom from anyone, or mission canceled)
   * - ``n_outbreak_duration_XXX``
     - Number of simulations with outbreak ends in day ``XXX``. Pre-quarantine days are not counted as outbreak. Outbreak can end at day 0 if the infectee will not show symtom or infect others.
   * - ``n_no_infected_by_seed``
     - Number of simulations when the introduced carrier does not infect anyone
   * - ``n_num_infected_by_seed_XXX``
     - Number of simulations with ``XXX`` people affected by the introduced virus carrier, ``XXX > 0`` .
   * - ``n_first_infected_by_seed_on_day_XXX``
     - Number of simulations when the introduced carrier infect the first infectee on day ``XXX``\ , ``XXX<1`` is rounded to 1, and so on. Pre-quarantine time is deducted.
   * - ``n_seed_show_no_symptom``
     - Number of simulations when the seed show no symptom
   * - ``n_seed_show_symptom_on_day_XXX``
     - Number of simulations when the carrier show symptom at day ``XXX``\ , ``XXX < 1`` is rounded to 1, and so on.
   * - ``n_no_first_infection``
     - Number of simualations with no infection at all.
   * - ``n_first_infection_on_day_XXX``
     - Number of simualations with the first infection event happens at day ``XXX``. It is the same as ``XXX_n_first_infected_by_seed_on_day`` but is reserved when multiple seeds are introduced.
   * - ``n_first_symptom``
     - Number of simulations when with at least one symptomatic case
   * - ``n_first_symptom_on_day_XXX``
     - Number of simulations when the first symptom appear at day ``XXX``\ , ``XXX < 1`` is rounded to 1, and so on. Symptom during quarantine is not considered and pre-quarantine days are deducted.
   * - ``n_second_symptom``
     - Number of simulations when there are a second symptomatic case symptom.
   * - ``n_second_symptom_on_day_XXX``
     - Number of simulations when the second symptom appear at day ``XXX`` **after the first symptom**
   * - ``n_third_symptom``
     - Number of simulations when there are a third symptomatic case symtom
   * - ``n_third_symptom_on_day_XXX``
     - Number of simulations when the first symptom appear at day ``XXX`` **after the second symptom**


Data analysis tools
-------------------

Because all the events have been recorded in the log files, it should not be too difficult for
you to write your own script (e.g. in R) to analyze them and produce nice figures. We however
made a small number of tools available. Please feel free to submit or own script for inclusion in the ``contrib``
library.

``time_vs_size.R``
^^^^^^^^^^^^^^^^^^^^^^

The `\ ``contrib/time_vs_size.R`` <https://github.com/ictr/covid19-outbreak-simulator/blob/master/contrib/time_vs_size.R>`_ script provides an example on how to process the data and produce
a figure. It can be used as follows:

.. code-block:: sh

   Rscript time_vs_size.R  simulation.log 'COVID19 Outbreak Simulation with Default Paramters' time_vs_size.png

and produces a figure


.. image:: https://raw.githubusercontent.com/ictr/covid19-outbreak-simulator/master/contrib/time_vs_size.png
   :target: https://raw.githubusercontent.com/ictr/covid19-outbreak-simulator/master/contrib/time_vs_size.png
   :alt: time_vs_size.png


``merge_summary.py``
^^^^^^^^^^^^^^^^^^^^^^^^

`\ ``contrib/merge_summary.py`` <https://github.com/ictr/covid19-outbreak-simulator/blob/master/contrib/merge_summary.py>`_ is a script to merge summary stats from multiple simulation runs.
