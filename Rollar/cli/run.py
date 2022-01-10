import os
import argparse
import time
import pathlib

from Rollar import Rollar_VERSION, Rollar_OBJ
import Rollar.config
import Rollar.logger
import Rollar.versions
import Rollar.scheduler
import Rollar.web
from Rollar.db import Rollardb

ERR_CODE = 1
ERR_CODE_NO_RESTART = 2


def build_args_parser(script_dir):
    """
    Build argument parser for Rollar.
    """

    parser = argparse.ArgumentParser(description='Rollar')
    parser.add_argument('-c', '--config', dest='cfg', type=str, default=pathlib.Path(script_dir).joinpath('config.ini'), required=False, help='configuration file to load.')
    parser.add_argument('--setup', dest='setup', type=str, required=False, nargs='?', const=True, default=False, help='Setup Configuration file.')
    parser.add_argument('--iliketobreakthings', dest='iliketobreakthings', type=str, nargs='?', const=True, required=False, default=False, help='Override Config Settings not meant to be overridden.')
    return parser.parse_args()


def run(settings, logger, db, script_dir, Rollar_web, versions, web, scheduler, deps):
    """
    Create Rollar object, and run threads.
    """

    rollar = Rollar_OBJ(settings, logger, db, versions, web, scheduler, deps)

    versions.sched_init(rollar)

    try:

        # Perform some actions now that HTTP Server is running
        rollar.api.get("/api/startup_tasks")

        # Run Scheduled Jobs thread
        rollar.scheduler.run()

        logger.noob("Rollar and Rollar_web should now be running and accessible via the web interface at %s" % rollar.api.base)
        if settings.dict["logging"]["level"].upper() == "NOOB":
            logger.noob("Set your [logging]level to INFO if you wish to see more logging output.")

        # wait forever
        restart_code = "restart"
        while rollar.threads["flask"].is_alive():
            time.sleep(1)

        if restart_code in ["restart"]:
            logger.noob("Rollar has been signaled to restart.")

        return restart_code

    except KeyboardInterrupt:
        return ERR_CODE_NO_RESTART

    return ERR_CODE


def start(args, script_dir, Rollar_web, deps):
    """
    Get Configuration for Rollar and start.
    """

    try:
        settings = Rollar.config.Config(args, script_dir)
    except Rollar.exceptions.ConfigurationError as e:
        print(e)
        return ERR_CODE_NO_RESTART

    # Setup Logging
    logger = Rollar.logger.Logger(settings)
    settings.logger = logger

    logger.noob("Loading Rollar %s with Rollar_web %s" % (Rollar_VERSION, Rollar_web.Rollar_web_VERSION))
    logger.info("Importing Core config values from Configuration File: %s" % settings.config_file)

    logger.debug("Logging to File: %s" % os.path.join(settings.internal["paths"]["logs_dir"], '.Rollar.log'))

    # Continue non-core settings setup
    settings.secondary_setup()

    scheduler = Rollar.scheduler.Scheduler()

    # Setup Database
    db = Rollardb(settings, logger)

    logger.debug("Setting Up shared Web Requests system.")
    web = Rollar.web.WebReq()

    # Setup Version System
    versions = Rollar.versions.Versions(settings, Rollar_web, logger, web, db, scheduler)

    return run(settings, logger, db, script_dir, Rollar_web, versions, web, scheduler, deps)


def config_setup(args, script_dir, Rollar_web):
    """
    Setup Config file.
    """

    settings = Rollar.config.Config(args, script_dir, Rollar_web)
    settings.setup_user_config()
    return ERR_CODE


def main(script_dir, Rollar_web, deps):
    """
    Rollar run script entry point.
    """

    try:
        args = build_args_parser(script_dir)

        if args.setup:
            return config_setup(args, script_dir, Rollar_web)

        while True:

            returned_code = start(args, script_dir, Rollar_web, deps)
            if returned_code not in ["restart"]:
                return returned_code

    except KeyboardInterrupt:
        print("\n\nInterrupted")
        return ERR_CODE


if __name__ == '__main__':
    """
    Trigger main function.
    """
    main()
