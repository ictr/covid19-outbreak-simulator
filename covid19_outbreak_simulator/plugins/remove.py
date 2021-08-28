import random

from covid19_outbreak_simulator.event import EventType
from covid19_outbreak_simulator.plugin import BasePlugin
from covid19_outbreak_simulator.utils import select_individuals


class remove(BasePlugin):

    # events that will trigger this plugin
    apply_at = "after_core_events"

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super().__init__(*args, **kwargs)

    def get_parser(self):
        parser = super().get_parser()
        parser.prog = "--plugin remove"
        parser.description = "remove individuals from the population"
        parser.add_argument("IDs", nargs="*", help="IDs of individuals to quarantine.")
        parser.add_argument(
            "--count",
            nargs="+",
            help="""Number of individuals to be removed, which can be from
            the entire population, or from specific groups
            (e.g. nurse=10) if there are groups.""",
        )
        parser.add_argument(
            "--target",
            nargs="*",
            help="""Type of individuals to be tested, can be "infected", "uninfected",
            "quarantined", "recovered", "vaccinated", "unvaccinated", or "all", or
            '!' of its negation, and any combination of '&' and '|' of these. If
            count is not specified, all matching individuals will be removed, otherwise
            count number will be removed, following the order of types. Default to "all".""",
        )
        return parser

    def apply(self, time, population, args=None):

        if not args.target and not args.IDs:
            raise RuntimeError(
                f"Please specify target of testing with parameter --target"
            )

        events = []
        if args.IDs:
            IDs = args.IDs
            if any(x not in population for x in IDs):
                raise ValueError("Invalid or non-existant ID to quarantine.")
            if args.target:
                IDs = select_individuals(population, IDs, args.target)
        else:
            for ps in args.count:
                name = ps.split("=", 1)[0] if "=" in ps else ""
                sz = int(ps.split("=", 1)[1]) if "=" in ps else int(ps)

                if name not in population.group_sizes:
                    raise ValueError(f"Subpopulation {name} does not exist")

                spIDs = [
                    x.id for x in population.individuals.values() if name in ("", x.group)
                ]
                IDs = select_individuals(population, spIDs, args.target, sz)

            for ID in IDs:
                population.remove(population[ID])
            removed_list = (
                f',removed={",".join(IDs[:sz])}' if args.verbosity > 1 else ""
            )
            if args.verbosity > 0:
                self.logger.write(
                    f"{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=remove,subpop={name},size={sz}{removed_list}\n"
                )
        return events
