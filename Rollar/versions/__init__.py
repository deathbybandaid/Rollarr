import os
import sys
import platform

from Rollar import Rollar_VERSION
from Rollar.tools import is_docker


class Versions():
    """
    Rollar versioning management system.
    """

    def __init__(self, settings, Rollar_web, logger, web, db, scheduler):
        self.Rollar_web = Rollar_web
        self.logger = logger
        self.web = web
        self.db = db
        self.scheduler = scheduler

        self.github_org_list_url = "https://api.github.com/orgs/Rollar/repos?type=all"
        self.github_plex_themes_core_info_url = "https://raw.githubusercontent.com/Rollar/Rollar/main/version.json"

        self.dict = {}

        self.register_plex_themes()

        self.register_env()

        self.get_online_versions()

        self.update_url = "/api/versions?method=check"

    def sched_init(self, plex_themes):
        """
        The Scheduled update method.
        """

        self.api = plex_themes.api
        self.scheduler.every(2).to(3).hours.do(self.sched_update)

    def sched_update(self):
        """
        Use an API thread to update Versions listing.
        """

        self.api.threadget(self.update_url)

    def get_online_versions(self):
        """
        Update Onling versions listing.
        """
        return

    def register_version(self, item_name, item_version, item_type):
        """
        Register a version item.
        """

        self.logger.debug("Registering %s item: %s %s" % (item_type, item_name, item_version))
        self.dict[item_name] = {
                                "name": item_name,
                                "version": item_version,
                                "type": item_type
                                }

    def register_plex_themes(self):
        """
        Register core version items.
        """

        self.register_version("Rollar", Rollar_VERSION, "Rollar")
        self.register_version("Rollar_web", self.Rollar_web.Rollar_web_VERSION, "Rollar")

    def register_env(self):
        """
        Register env version items.
        """

        self.register_version("Python", sys.version, "env")
        if sys.version_info.major == 2 or sys.version_info < (3, 7):
            self.logger.error('Error: Rollar requires python 3.7+. Do NOT expect support for older versions of python.')

        opersystem = platform.system()
        self.register_version("Operating System", opersystem, "env")

        if opersystem in ["Linux", "Darwin"]:

            # Linux/Mac
            if os.getuid() == 0 or os.geteuid() == 0:
                self.logger.warning('Do not run Rollar with root privileges.')

        elif opersystem in ["Windows"]:

            # Windows
            if os.environ.get("USERNAME") == "Administrator":
                self.logger.warning('Do not run Rollar as Administrator.')

        else:
            self.logger.warning("Uncommon Operating System, use at your own risk.")

        isdocker = is_docker()
        self.register_version("Docker", isdocker, "env")
