# coding=utf-8

Rollar_VERSION = "v0.9.0-beta"


class Rollar_INT_OBJ():

    def __init__(self, settings, logger, db, versions, web, scheduler, deps):
        """
        An internal catalogue of core methods.
        """

        self.version = Rollar_VERSION
        self.versions = versions
        self.config = settings
        self.logger = logger
        self.db = db
        self.web = web
        self.scheduler = scheduler
        self.deps = deps


class Rollar_OBJ():

    def __init__(self, settings, logger, db, versions, web, scheduler, deps):
        """
        The Core Backend.
        """

        logger.info("Initializing Rollar_OBJ Core Functions.")
        self.rollar = Rollar_INT_OBJ(settings, logger, db, versions, web, scheduler, deps)

    def __getattr__(self, name):
        """
        Quick and dirty shortcuts. Will only get called for undefined attributes.
        """

        if hasattr(self.rollar, name):
            return eval("self.rollar.%s" % name)
