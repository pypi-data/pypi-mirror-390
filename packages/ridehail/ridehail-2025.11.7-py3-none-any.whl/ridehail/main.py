#!/usr/bin/env python3
"""
Main entry point for ridehail simulation application.
Self-contained entry point for PyApp distribution - contains all run.py functionality.
"""

import logging
import logging.config
import sys
from ridehail.atom import Animation
from ridehail.animation import create_animation
from ridehail.config import RideHailConfig
from ridehail.simulation import RideHailSimulation
from ridehail.sequence import RideHailSimulationSequence

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": True,
    }
)


def main():
    """
    Entry point - matches original run.py exactly.
    """
    ridehail_config = RideHailConfig()
    if ridehail_config:
        if (
            hasattr(ridehail_config, "run_sequence")
            and ridehail_config.run_sequence.value
        ):
            seq = RideHailSimulationSequence(ridehail_config)
            seq.run_sequence(ridehail_config)
        else:
            sim = RideHailSimulation(ridehail_config)
            if (
                ridehail_config.animate.value is False
                or ridehail_config.animation_style.value
                in (Animation.NONE, Animation.TEXT, "none", "text")
            ):
                sim.simulate()
            else:
                # Use the animation factory (Textual is now default for terminal animations)
                anim = create_animation(
                    ridehail_config.animation_style.value,
                    sim,
                )
                anim.animate()
        return 0
    else:
        logging.error("Configuration error: exiting")
        return -1


def main_with_profiling():
    """Main entry point with optional profiling support - matches original run.py"""
    if "--profile" in sys.argv:
        import cProfile
        import pstats

        profiler = cProfile.Profile()
        profiler.enable()
        main()
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats("tottime")
        stats.print_stats()
    else:
        sys.exit(main())


if __name__ == "__main__":
    main_with_profiling()