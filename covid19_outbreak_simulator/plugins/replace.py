import random

from covid19_outbreak_simulator.event import Event, EventType
from covid19_outbreak_simulator.plugin import BasePlugin
from covid19_outbreak_simulator.utils import select_individuals


class replace(BasePlugin):

    # events that will trigger this plugin
    apply_at = "after_core_events"

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super().__init__(*args, **kwargs)

    def get_parser(self):
        parser = super().get_parser()
        parser.prog = "--plugin replace"
        parser.description = (
            """replace individuals with refresh individuals, with allow
            keeping some of them properties such as vaccination status""",
        )
        parser.add_argument("IDs", nargs="*", help="IDs of individuals to quarantine.")
        parser.add_argument(
            "--count",
            nargs="+",
            help="""Number of individuals to be replaced, which can be from
            the entire population, or from specific groups
            (e.g. nurse=10) if there are groups.""",
        )
        parser.add_argument(
            "--target",
            nargs="*",
            help="""Type of individuals to be tested, can be "infected", "uninfected",
            "quarantined", "recovered", "vaccinated", "unvaccinated", or "all", or
            '!' of its negation, and any combination of '&' and '|' of these. If
            count is not specified, all matching individuals will be replaced, otherwise
            count number will be replaced, following the order of types. Default to "all".""",
        )
        parser.add_argument(
            "--duration",
            type=float,
            help="""Duration of replacement, default to no replacement
                back""",
        )
        parser.add_argument(
            "--keep",
            nargs="*",
            help="""Properties to be passed on to the replacement individuals,
            for example "vaccinated" to keep the vaccination status of the replacement
            individual,""",
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
                    x.id
                    for x in population.individuals.values()
                    if name in ("", x.group)
                ]
                IDs = select_individuals(population, spIDs, args.target, sz)

            for ID in IDs:
                events.append(
                    Event(
                        time,
                        EventType.REPLACEMENT,
                        reason="plugin",
                        till=time + args.duration
                        if args.duration is not None
                        else None,
                        keep=[] if args.keep is None else args.keep,
                        target=population[ID],
                        logger=self.logger,
                    )
                )
            replaced_list = (
                f',replaced={",".join(IDs[:sz])}' if args.verbosity > 1 else ""
            )
            if args.verbosity > 0:
                self.logger.write(
                    f"{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=replace,subpop={name},size={sz}{replaced_list}\n"
                )
        return events
