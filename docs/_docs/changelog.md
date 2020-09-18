---
title: Change Log
permalink: /docs/changelog/
---

## Version 0.3.3

* Fix negative recovery time for `leadtime == any`.
* Improve plugin `insert` for adding individuals to population.
* Add plugin `community_spread`
* Add `contrib/report2csv.py`.
* Fix quarantine with leadtime.

## Version 0.3.0

* A new plugin system that can be triggered by options `--begin`, `--end`, `--interval`, `--at`, and `--trigger-by`.
* Add a number of system plugins including `init`, `sample`, `setparam`, and `quarantine`, some of them are separated from the simulator core.

## Version 0.2.0

* Generate reports from log files to make it easier to generate statistics
* Add contrib directory to facilitate data analysis.

## Version 0.1.0

* Initial release