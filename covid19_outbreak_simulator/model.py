import os
import re
from fnmatch import fnmatch

import numpy as np
import pandas as pd
import yaml
from scipy.optimize import bisect
from scipy.stats import norm
from .event import EventType
from covid19_outbreak_simulator.utils import as_float, as_int


class Params:
    def __init__(self, args=None):
        # args should be args returned from argparser
        self.params = {
            "simulation_interval",
            "prop_asym_carriers",
            "incubation_period",
            "symptomatic_r0",
            "asymptomatic_r0",
            "susceptibility",
            "symptomatic_transmissibility_model",
            "asymptomatic_transmissibility_model",
            "immunity_of_recovered",
            "infectivity_of_recovered",
        }
        self.groups = {}
        self.set_params(args)

    def __str__(self):
        def float_representer(dumper, value):
            text = "{0:.4f}".format(value)
            return dumper.represent_scalar("tag:yaml.org,2002:float", text)

        yaml.add_representer(float, float_representer)

        val = {
            x: list(y) if isinstance(y, set) else y
            for x, y in self.__dict__.items()
            if x != "params"
        }
        if "groups" in val and len(val["groups"]) == 1:
            val["groups"] = {"Unnamed": list(val["groups"].values())[0]}
        return yaml.dump(val, sort_keys=True, indent=4)

    def set(self, param, prop, value):
        if param not in self.params:
            raise ValueError(f"Unrecgonzied parameter {param}")
        if prop is None or prop == "self":
            setattr(self, param, value)
        elif prop in ("loc", "low", "high", "mean", "sigma", "scale"):
            setattr(self, f"{param}_{prop}", value)
        elif prop.startswith("multiplier_"):
            group = prop[11:]
            if group != "" and group not in self.groups:
                raise ValueError(
                    f'Group {group} does not exist for parameter {param}. Available groups are: {", ".join(self.groups.keys())}'
                )
            if value < 0:
                raise ValueError(f"Multiplier should be positive {value} specified")
            if group == "":
                for grp in self.groups:
                    setattr(self, f"{param}_{prop}{group}", value)
            else:
                setattr(self, f"{param}_{prop}", value)
        elif re.match("quantile_(.*)", prop):
            lq = float(re.match("quantile_(.*)", prop)[1]) / 100
            loc = getattr(self, f"{param}_loc")
            if loc == value:
                setattr(self, f"{param}_scale", 0)
            else:
                sd = bisect(
                    lambda x: norm.cdf(value, loc=loc, scale=x) - lq, a=0.00001, b=25
                )
                setattr(self, f"{param}_scale", sd)
        else:
            raise ValueError(f"Unrecognized property {prop}")

    def check_id(self, ID):
        if ID.isnumeric():
            if "" not in self.groups:
                raise ValueError(f"Invalid ID {ID}: No default group.")
            if int(ID) >= self.groups[""] or int(ID) < 0:
                raise ValueError(f"Invalid ID {ID}: Index out of range.")
        else:
            if "_" not in ID:
                raise ValueError(
                    f"index or group_index is expected for individual ID: {ID} provided"
                )
            grp, idx = ID.rsplit("_")
            if grp not in self.groups:
                raise ValueError(f"Invalid ID {ID}")
            if int(idx) >= self.groups[grp] or int(idx) < 0:
                raise ValueError(f"Invalid ID {idx}: Index out of range.")

    def set_popsize(self, val):
        if not val:
            return
        for ps in val:
            if "=" in ps:
                name, size = ps.split("=", 1)
            else:
                name = ""
                size = ps
            size = as_int(size)
            if name == "all":
                raise ValueError(
                    'Group name "all" is reserved for the entire population.'
                )
            if name in self.groups:
                raise ValueError(f'Group "{name}" has been specified before')
            self.groups[name] = size

    def set_infectors(self, val):
        if not val:
            return
        for ID in val:
            self.check_id(ID)

    def _set_multiplier(self, multiplier, param_name):
        name, value = multiplier.split("=", 1)
        value = as_float(value, "Multiplier should have format name=float_value")
        if name == "all":
            self.set(param_name, "multiplier_", value)
        else:
            names = [x for x, y in self.groups.items() if fnmatch(x, name)]
            if not names:
                raise ValueError(
                    f"Invalid group name {name} in multiplier {multiplier}"
                )
            for name in names:
                self.set(param_name, f"multiplier_{name}", value)

    def set_symptomatic_r0(self, val):
        if not val:
            return
        # if asymptomatic_r0 is specified, it should a number of a range...
        pars = [x for x in val if "=" not in x]
        if len(pars) == 1:
            self.set(
                "symptomatic_r0",
                "loc",
                as_float(
                    pars[0],
                    "The symptomatic_r0 should be a float number, if it is not a multiplier for groups",
                ),
            )
            self.set("symptomatic_r0", "scale", 0.0)
        elif len(pars) == 2:
            p0 = as_float(
                pars[0],
                "The symptomatic_r0 should be a float number, if it is not a multiplier for groups",
            )
            p1 = as_float(
                pars[1],
                "The symptomatic_r0 should be a float number, if it is not a multiplier for groups",
            )
            self.set("symptomatic_r0", "loc", (p0 + p1) / 2)
            self.set("symptomatic_r0", "quantile_2.5", p0)

        elif len(pars) > 2:
            raise ValueError("The symptomatic_r0 should be one or two float number.")
        #
        for multiplier in [x for x in val if "=" in x]:
            self._set_multiplier(multiplier, "symptomatic_r0")

    def set_asymptomatic_r0(self, val):
        if not val:
            return
        # if asymptomatic_r0 is specified, it should a number of a range...
        pars = [x for x in val if "=" not in x]
        if len(pars) == 1:
            self.set(
                "asymptomatic_r0",
                "loc",
                as_float(
                    pars[0],
                    "The asymptomatic_r0 should be a float number, if it is not a multiplier for groups",
                ),
            )
            self.set("asymptomatic_r0", "scale", 0.0)
        elif len(pars) == 2:
            p0 = as_float(
                pars[0],
                "The asymptomatic_r0 should be a float number, if it is not a multiplier for groups",
            )
            p1 = as_float(
                pars[1],
                "The asymptomatic_r0 should be a float number, if it is not a multiplier for groups",
            )
            self.set("asymptomatic_r0", "loc", (p0 + p1) / 2)
            self.set(
                "asymptomatic_r0",
                "quantile_2.5",
                p0,
            )
        elif len(pars) > 2:
            raise ValueError("The asymptomatic_r0 should be one or two float number.")
        #
        for multiplier in [x for x in val if "=" in x]:
            self._set_multiplier(multiplier, "asymptomatic_r0")

    def set_incubation_period(self, val):
        if not val:
            return

        pars = [x for x in val if x in ("normal", "lognormal") or "=" not in x]
        if pars:
            if pars[0] in ("normal", "lognormal"):
                self.set(
                    "incubation_period",
                    "mean" if pars[0] == "lognormal" else "loc",
                    as_float(
                        pars[1],
                        "Second parameter of incubation_period should be a float number",
                    ),
                )
                self.set(
                    "incubation_period",
                    "sigma" if pars[0] == "lognormal" else "scale",
                    as_float(
                        pars[2],
                        "Third parameter of lognormal incubation_period should be a float number",
                    ),
                )
            elif len(pars) == 1:
                self.set(
                    "incubation_period",
                    "mean",
                    np.log(
                        as_float(
                            pars[0],
                            "First parameter of incubation_period should be a float number if not model name",
                        )
                    )
                    - 1 / 2 * 0.418 ** 2,
                )
                self.set("incubation_period", "sigma", 0.418)
            else:
                raise ValueError("Unacceptable specification of incubation period")

        # multipliers
        for multiplier in [x for x in val if "=" in x]:
            self._set_multiplier(multiplier, "incubation_period")

    # def normal_parameters(x1, p1, x2, p2):
    #     "Find parameters for a normal random variable X so that P(X < x1) = p1 and P(X < x2) = p2."
    #     denom = stats.norm.ppf(p2) - stats.norm.ppf(p1)
    #     sigma = (x2 - x1) / denom
    #     mu = (x1*stats.norm.ppf(p2) - x2*stats.norm.ppf(p1)) / denom
    #     return (mu, sigma)
    #
    # n = 3.5
    # a, b = normal_parameters(math.log(10-n), 0.88, math.log(15-n), 0.95)
    # rng = np.random.lognormal(a, b, 10000)
    # rng = pd.Series(rng)
    # rng.hist(bins=30)
    # [n + rng.quantile(x) for x in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.975]]
    # a, b

    def set_symptomatic_transmissibility_model(self, val):
        if not val or val[0] != "piecewise":
            raise ValueError("Only a piecewise model is supported")

        if len(val) == 1:
            self.symptomatic_transmissibility_model = dict(
                name=val[0],
                noninfectivity_proportion=0.2,
                peak_proportion=2 / 3.0,
                duration_shift=2,
                duration_mean=0.8653416550012768,
                duration_sigma=1.0332881142805803,
            )

        elif len(val) != 6:
            raise ValueError(
                f"""Parameter --symptomatic-transmissibility-model should be
                specified as "piecewise" followed by with time for start of infectivity,
                time for peak of infectivity (both proportional to total incubation period)),
                miniaml duration after incubation, and parameters for a lognormal distribution that
                determines the duration of infectivity. "{' '.join(val)}" (length {len(val)}) provided"""
            )
        else:
            self.symptomatic_transmissibility_model = dict(
                name=val[0],
                noninfectivity_proportion=as_float(val[1]),
                peak_proportion=as_float(val[2]),
                duration_shift=as_float(val[3]),
                duration_mean=as_float(val[4]),
                duration_sigma=as_float(val[5]),
            )

    # n = 1
    # a, b = normal_parameters(math.log(2-n), 0.025, math.log(8-n), 0.975)
    # rng = np.random.lognormal(a, b, 10000)
    # rng = pd.Series(rng)
    # rng.hist(bins=30)
    # [n + rng.quantile(x) for x in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.975]]

    def set_asymptomatic_transmissibility_model(self, val):
        if not val or val[0] != "piecewise":
            raise ValueError("Only a piecewise model is supported")
        if len(val) == 1:
            self.asymptomatic_transmissibility_model = dict(
                name=val[0],
                noninfectivity_proportion=0.1,
                peak_proportion=0.4,
                duration_shift=3,
                duration_mean=0.9729550745276567,
                duration_sigma=0.49641477200713996,
            )
        elif len(val) != 6:
            raise ValueError(
                f"""Parameter --asymptomatic-transmissibility-model should be
                specified as "piecewise" followed by with time for start of infectivity,
                time for peak of infectivity (both proportional to total duration)),
                miniaml duration, and parameters for a lognormal distribution that
                determines the duration of infectivity: "{' '.join(val)}"" (length {len(val)}) provided"""
            )
        else:
            self.asymptomatic_transmissibility_model = dict(
                name=val[0],
                noninfectivity_proportion=as_float(val[1]),
                peak_proportion=as_float(val[2]),
                duration_shift=as_float(val[3]),
                duration_mean=as_float(val[4]),
                duration_sigma=as_float(val[5]),
            )

    def set_susceptibility(self, val):
        if not val:
            return
        base = [x for x in val if not isinstance(x, str) or "=" not in x]
        if not base:
            self.set("susceptibility", "mean", 1.0)
        elif len(base) > 1:
            raise ValueError("Susceptibility should be a single number.")
        else:
            base_val = as_float(base[0], "Susceptibility should be a float number")
            if base_val > 1 or base_val < 0:
                raise ValueError("suscepbility should be betwee 0 and 1: {base_val}")
            self.set("susceptibility", "mean", base_val)

        for multiplier in [x for x in val if isinstance(x, str) and "=" in x]:
            self._set_multiplier(multiplier, "susceptibility")

    def set_prop_asym_carriers(self, val):
        if not val:
            return
        try:
            pars = [float(x) for x in val if "=" not in x]
        except Exception as e:
            raise ValueError(
                f'Paramter prop-asym-carriers expect one or two float value or multipliers: {" ".join(val)} provided'
            ) from e
        if len(pars) == 1:
            self.set("prop_asym_carriers", "loc", as_float(pars[0]))
            self.set("prop_asym_carriers", "scale", 0)
        elif len(pars) == 2:
            if pars[0] > pars[1]:
                raise ValueError(
                    "Proportions for parameter prop-asym-carriers should be incremental."
                )
            self.set("prop_asym_carriers", "loc", (pars[0] + pars[1]) / 2)
            self.set("prop_asym_carriers", "quantile_2.5", pars[0])
        elif len(pars) > 2:
            raise ValueError("Parameter prop-asym-carriers accepts one or two numbers.")
        #
        for multiplier in [x for x in val if "=" in x]:
            self._set_multiplier(multiplier, "prop_asym_carriers")

    def set_immunity_of_recovered(self, val):
        if not val:
            return
        if len(val) == 1:
            self.set("immunity_of_recovered", "self", [val[0], val[0]])
        elif len(val) == 2:
            self.set("immunity_of_recovered", "self", val)
        else:
            raise ValueError(
                "Immunity of recovered should be an array of one or two values."
            )

    def set_infectivity_of_recovered(self, val):
        if not val:
            return
        if len(val) == 1:
            self.set("infectivity_of_recovered", "self", [val[0], val[0]])
        elif len(val) == 2:
            self.set("infectivity_of_recovered", "self", val)
        else:
            raise ValueError(
                "Infectivity of recovered should be an array of one or two values."
            )

    def set_params(self, args):
        # set some default values first
        self.set("simulation_interval", "self", args.interval if args else 1 / 24)
        self.set("immunity_of_recovered", "self", [0.99, 0.99])
        self.set("infectivity_of_recovered", "self", [1, 1])
        self.set("prop_asym_carriers", "loc", 0.4)
        self.set("prop_asym_carriers", "scale", 0)
        self.set("symptomatic_r0", "loc", (1.4 + 2.8) / 2)
        self.set("symptomatic_r0", "quantile_2.5", 1.4)
        self.set("asymptomatic_r0", "loc", (1.4 + 2.8) * 0.75 / 2)
        self.set("asymptomatic_r0", "quantile_2.5", 1.4 * 0.75)
        self.set("incubation_period", "mean", 1.621)
        self.set("incubation_period", "sigma", 0.418)

        if not args:
            self.set_symptomatic_transmissibility_model(["piecewise"])
            self.set_asymptomatic_transmissibility_model(["piecewise"])
            return

        self.set_popsize(args.popsize)
        self.set_infectors(args.infectors)
        # modify from command line args
        self.set_symptomatic_r0(args.symptomatic_r0)
        self.set_asymptomatic_r0(args.asymptomatic_r0)
        self.set_incubation_period(args.incubation_period)
        self.set_symptomatic_transmissibility_model(
            args.symptomatic_transmissibility_model
        )
        self.set_asymptomatic_transmissibility_model(
            args.asymptomatic_transmissibility_model
        )
        self.set_susceptibility(args.susceptibility)
        self.set_prop_asym_carriers(args.prop_asym_carriers)
        self.set_immunity_of_recovered(args.immunity_of_recovered)
        self.set_infectivity_of_recovered(args.infectivity_of_recovered)


class Model(object):

    sd_5 = bisect(lambda x: norm.cdf(10, loc=5, scale=x) - 0.995, a=0.001, b=5)
    sd_6 = bisect(lambda x: norm.cdf(14, loc=6, scale=x) - 0.975, a=0.001, b=5)

    def __init__(self, params):
        self.params = params
        self.params.prop_asym_carriers = None

    def draw_prop_asym_carriers(self, group=""):
        self.params.prop_asym_carriers = np.random.normal(
            loc=self.params.prop_asym_carriers_loc,
            scale=self.params.prop_asym_carriers_scale,
        )
        return min(
            max(
                self.params.prop_asym_carriers
                * getattr(self.params, f"prop_asym_carriers_multiplier_{group}", 1.0),
                0,
            ),
            1,
        )

    def draw_is_asymptomatic(self):
        return np.random.uniform(0, 1) < self.params.prop_asym_carriers

    def draw_random_r0(self, symptomatic, group=""):
        """
        Reproduction number, drawn randomly between 1.4 and 2.8.
        """
        if symptomatic:
            if self.params.symptomatic_r0_scale == 0.0:
                return self.params.symptomatic_r0_loc
            else:
                return max(
                    0,
                    np.random.normal(
                        self.params.symptomatic_r0_loc, self.params.symptomatic_r0_scale
                    ),
                )
        else:
            if self.params.asymptomatic_r0_scale == 0.0:
                return self.params.asymptomatic_r0_loc
            else:
                return max(
                    0,
                    np.random.normal(
                        self.params.asymptomatic_r0_loc,
                        self.params.asymptomatic_r0_scale,
                    ),
                )

    def draw_random_incubation_period(self, group=""):
        """
        Incubation period, drawn from a lognormal distribution.
        """
        if hasattr(self.params, "incubation_period_loc"):
            # if a normal distribution is specified
            ip = max(
                0,
                np.random.normal(
                    loc=self.params.incubation_period_loc,
                    scale=self.params.incubation_period_scale,
                ),
            )
        else:
            ip = np.random.lognormal(
                mean=self.params.incubation_period_mean,
                sigma=self.params.incubation_period_sigma,
            )
        return ip * getattr(self.params, f"incubation_period_multiplier_{group}", 1.0)

    def draw_infection_params(self, symptomatic, vaccinated=None):
        if symptomatic:
            # duration of infection is 8 days after incubation
            return {
                "duration": self.params.symptomatic_transmissibility_model[
                    "duration_shift"
                ]
                + np.random.lognormal(
                    self.params.symptomatic_transmissibility_model["duration_mean"],
                    self.params.symptomatic_transmissibility_model["duration_sigma"],
                ),
                "vaccinated": vaccinated,
            }
        else:
            # 12 day overall (with normal at 4.8)
            return {
                "duration": self.params.asymptomatic_transmissibility_model[
                    "duration_shift"
                ]
                + np.random.lognormal(
                    self.params.asymptomatic_transmissibility_model["duration_mean"],
                    self.params.asymptomatic_transmissibility_model["duration_sigma"],
                ),
                "vaccinated": vaccinated,
            }

    def get_symptomatic_transmission_probability(self, incu, R0, params):
        """Transmission probability.
        incu
            incubation period in days (can be float)

        R0
            reproductive number, which is the expected number of infectees

        interval
            interval of simulation, default to 1/24, which is by hours

        returns

        x
            time point
        y
            probability of transmission for each time point
        """
        duration = incu + params["duration"]
        #
        x = np.linspace(0, duration, int(duration / self.params.simulation_interval))
        infect_time = (
            incu
            * self.params.symptomatic_transmissibility_model[
                "noninfectivity_proportion"
            ]
        )
        peak_time = (
            incu * self.params.symptomatic_transmissibility_model["peak_proportion"]
        )

        y = np.piecewise(
            x,
            [x < infect_time, (x >= infect_time) & (x < peak_time), x >= peak_time],
            [
                0,
                lambda t: (t - infect_time) / (peak_time - infect_time),
                lambda t: (duration - t) / (duration - peak_time),
            ],
        )
        y = np.minimum(y / sum(y) * R0, 1)
        if params["vaccinated"]:
            duration = duration * 0.75
            x = np.linspace(
                0, duration, int(duration / self.params.simulation_interval)
            )
            if peak_time < duration:
                # from peak_time to duration, drop to zero
                y_max = max(y)
                y = np.piecewise(
                    x,
                    [
                        x < infect_time,
                        (x >= infect_time) & (x < peak_time),
                        x >= peak_time,
                    ],
                    [
                        0,
                        lambda t: y_max * (t - infect_time) / (peak_time - infect_time),
                        lambda t: y_max * (duration - t) / (duration - peak_time),
                    ],
                )
        return x, y

    def get_asymptomatic_transmission_probability(self, R0, params):
        """Asymptomatic Transmission probability.
        R0
            reproductive number, which is the expected number of infectees

        interval
            interval of simulation, default to 1/24, which is by hours

        returns

        x
            time point
        y
            probability of transmission for each time point
        """
        duration = params["duration"]
        #
        x = np.linspace(0, duration, int(duration / self.params.simulation_interval))
        infect_time = (
            duration
            * self.params.asymptomatic_transmissibility_model[
                "noninfectivity_proportion"
            ]
        )
        peak_time = (
            duration
            * self.params.asymptomatic_transmissibility_model["peak_proportion"]
        )

        y = np.piecewise(
            x,
            [x < infect_time, (x >= infect_time) & (x < peak_time), x >= peak_time],
            [
                0,
                lambda y: (y - infect_time) / (peak_time - infect_time),
                lambda y: (duration - y) / (duration - peak_time),
            ],
        )
        y = np.minimum(y / sum(y) * R0, 1)
        # we assume that viral load is 2 times the transmissibility
        # for asymptomatic cases.
        if params["vaccinated"]:
            duration = duration * 0.75
            x = np.linspace(
                0, duration, int(duration / self.params.simulation_interval)
            )
            if peak_time < duration:
                # from peak_time to duration, drop to zero
                y_max = max(y)
                y = np.piecewise(
                    x,
                    [
                        x < infect_time,
                        (x >= infect_time) & (x < peak_time),
                        x >= peak_time,
                    ],
                    [
                        0,
                        lambda t: y_max * (t - infect_time) / (peak_time - infect_time),
                        lambda t: y_max * (duration - t) / (duration - peak_time),
                    ],
                )
        return x, y


def print_proportion(data, name):
    series = pd.Series(data)
    print("\n" + name + ":")
    print(f"      proportion:  {series.mean():.4f}")


def print_stats(data, name):
    series = pd.Series(data)
    print("\n" + name + ":")
    print(f"            mean:  {series.mean():.4f}")
    print(f"             std:  {series.std():.4f}")
    #for q in (0.025, 0.05, 0.5, 0.95, 0.975):
    #    print(f"  {q*100:4.1f}% quantile:  {series.quantile(q):.4f}")


def print_cnt(data, name):
    nums = sorted(list(set(data)))
    print("\n" + name + ":")
    for n in nums:
        print(f"    {n}:\t{data.count(n)/len(data)*100:.1f}%")


def sample_prop_asymp_carriers(model, N=1000):
    asym_carriers = []
    for _ in range(N):
        model.draw_prop_asym_carriers()
        asym_carriers.append(model.draw_is_asymptomatic())
    return asym_carriers


def summarize_model(args):
    from .population import Individual

    params = Params(args)
    print("Parameters (in YAML format)\n")
    print(params)
    print()
    #
    print("Properties:")
    N = 5000
    model = Model(params)
    print_proportion(
        sample_prop_asymp_carriers(model, N), "Proportion of asymptomatic carriers"
    )

    #
    model.params.set("prop_asym_carriers", "loc", 0)
    model.params.set("prop_asym_carriers", "scale", 0)
    print_stats(
        [model.draw_random_incubation_period() for x in range(N)], "Incubation period"
    )

    print_stats(
        [model.draw_random_r0(symptomatic=True) for x in range(N)],
        "Production Number (Symptomatic)",
    )
    print_stats(
        [model.draw_random_r0(symptomatic=False) for x in range(N)],
        "Production Number (Asymptomatic)",
    )

    model.params.set("prop_asym_carriers", "loc", 0)
    model.params.set("prop_asym_carriers", "scale", 0)

    cp = []
    du = []
    cnt = []
    with open(os.devnull, "w") as logger:
        logger.id = 1
        model.draw_prop_asym_carriers()
        for _ in range(N):
            ind = Individual(id="0", susceptibility=1, model=model, logger=logger)
            evts = ind.symptomatic_infect(time=0, by=None, handle_symptomatic=["keep"])
            cnt.append(len([x for x in evts if x.action == EventType.INFECTION]))
            cp.append(ind.communicable_period())
            du.append(ind.total_duration())

    model.params.set("prop_asym_carriers", "loc", 1)
    model.params.set("prop_asym_carriers", "scale", 0)

    acp = []
    adu = []
    acnt = []
    with open(os.devnull, "w") as logger:
        logger.id = 1
        model.draw_prop_asym_carriers()
        for _ in range(N):
            ind = Individual(id="0", susceptibility=1, model=model, logger=logger)
            evts = ind.asymptomatic_infect(time=0, by=None, handle_symptomatic=["keep"])
            acnt.append(len([x for x in evts if x.action == EventType.INFECTION]))
            acp.append(ind.communicable_period())
            adu.append(ind.total_duration())

    print_stats(cp, "Communicable Period (Symptomatic)")
    print_stats(du, "Total Duration (Symptomatic)")
    print_cnt(cnt, "Number of infections (Symptomatic)")
    print_stats(acp, "Communicable Period (Asymptomatic)")
    print_stats(adu, "Total Duration (Asymptomatic)")
    print_cnt(acnt, "Number of infections (Asymptomatic)")


    model.params.set("prop_asym_carriers", "loc", 0)
    model.params.set("prop_asym_carriers", "scale", 0)

    cp = []
    du = []
    cnt = []
    with open(os.devnull, "w") as logger:
        logger.id = 1
        model.draw_prop_asym_carriers()
        for _ in range(N):
            ind = Individual(id="0", susceptibility=1, model=model, logger=logger)
            ind.vaccinate(0, immunity=[0.75, 0.75], infectivity=[1, 1])
            evts = ind.symptomatic_infect(time=0, by=None, handle_symptomatic=["keep"])
            cnt.append(len([x for x in evts if x.action == EventType.INFECTION]))
            cp.append(ind.communicable_period())
            du.append(ind.total_duration())

    model.params.set("prop_asym_carriers", "loc", 1)
    model.params.set("prop_asym_carriers", "scale", 0)

    acp = []
    adu = []
    acnt = []
    with open(os.devnull, "w") as logger:
        logger.id = 1
        model.draw_prop_asym_carriers()
        for _ in range(N):
            ind = Individual(id="0", susceptibility=1, model=model, logger=logger)
            ind.vaccinate(0, immunity=[0.75, 0.75], infectivity=[1, 1])
            evts = ind.asymptomatic_infect(time=0, by=None, handle_symptomatic=["keep"])
            acnt.append(len([x for x in evts if x.action == EventType.INFECTION]))
            acp.append(ind.communicable_period())
            adu.append(ind.total_duration())

    print_stats(cp, "Communicable Period (Symptomatic Vaccinated)")
    print_stats(du, "Total Duration (Symptomatic Vaccinated)")
    print_cnt(cnt, "Number of infections (Symptomatic Vaccinated)")
    print_stats(acp, "Communicable Period (Asymptomatic Vaccinated)")
    print_stats(adu, "Total Duration (Asymptomatic Vaccinated)")
    print_cnt(acnt, "Number of infections (Asymptomatic Vaccinated)")

    model.params.set("prop_asym_carriers", "loc", 0)
    model.params.set("prop_asym_carriers", "scale", 0)

    si = []
    gt = []

    with open(os.devnull, "w") as logger:
        logger.id = 1
        model.draw_prop_asym_carriers()
        for _ in range(N):
            ind = Individual(id="0", susceptibility=1, model=model, logger=logger)
            evts = ind.symptomatic_infect(time=0, by=None, handle_symptomatic=["keep"])
            for evt in [x for x in evts if x.action.name == "INFECTION"]:
                gt.append(evt.time)
                si.append(
                    evt.time
                    + ind.model.draw_random_incubation_period()
                    - ind.incubation_period
                )
                break

    print_stats(si, "Serial Interval")
    print_stats(gt, "Generation Time")
