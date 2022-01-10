# coding=utf-8

import json
import os.path
import traceback

from sqlalchemy import Column, create_engine, String, Text
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


def _deserialize(value):

    if value is None:
        return None

    # sqlite likes to return ints for strings that look like ints, even though
    # the column type is string. That's how you do dynamic typing wrong.
    value = str(value)

    # Just in case someone's mucking with the DB in a way we can't account for,
    # ignore json parsing errors
    try:
        value = json.loads(value)
    except ValueError:
        pass
    return value


BASE = declarative_base()
MYSQL_TABLE_ARGS = {'mysql_engine': 'InnoDB',
                    'mysql_charset': 'utf8mb4',
                    'mysql_collate': 'utf8mb4_unicode_ci'}


class RollarValues(BASE):
    __tablename__ = 'plex_themes_values'
    __table_args__ = MYSQL_TABLE_ARGS
    item = Column(String(255), primary_key=True)
    namespace = Column(String(255), primary_key=True)
    key = Column(String(255), primary_key=True)
    value = Column(Text())


class Rollardb(object):
    """
    The Database system for Rollar.
    """

    def __init__(self, settings, logger):
        self.config = settings
        self.logger = logger

        # MySQL - mysql://username:password@localhost/db
        # SQLite - sqlite:////cache/path/default.db
        self.type = self.config.dict["database"]["type"]

        # Handle SQLite explicitly as a default
        if self.type == 'sqlite':
            path = self.config.dict["database"]["path"]
            path = os.path.expanduser(path)
            self.filename = path
            self.url = 'sqlite:///%s' % path
        # Otherwise, handle all other database engines
        else:
            query = {}
            if self.type == 'mysql':
                drivername = self.config.dict["database"]["driver"] or 'mysql'
                query = {'charset': 'utf8mb4'}
            elif self.type == 'postgres':
                drivername = self.config.dict["database"]["driver"] or 'postgresql'
            elif self.type == 'oracle':
                drivername = self.config.dict["database"]["driver"] or 'oracle'
            elif self.type == 'mssql':
                drivername = self.config.dict["database"]["driver"] or 'mssql+pymssql'
            elif self.type == 'firebird':
                drivername = self.config.dict["database"]["driver"] or 'firebird+fdb'
            elif self.type == 'sybase':
                drivername = self.config.dict["database"]["driver"] or 'sybase+pysybase'
            else:
                raise Exception('Unknown db_type')

            db_user = self.config.dict["database"]["user"]
            db_pass = self.config.dict["database"]["pass"]
            db_host = self.config.dict["database"]["host"]
            db_port = self.config.dict["database"]["port"]  # Optional
            db_name = self.config.dict["database"]["name"]  # Optional, depending on DB

            # Ensure we have all our variables defined
            if db_user is None or db_pass is None or db_host is None:
                raise Exception('Please make sure the following core '
                                'configuration values are defined: '
                                'db_user, db_pass, db_host')
            self.url = URL(drivername=drivername, username=db_user,
                           password=db_pass, host=db_host, port=db_port,
                           database=db_name, query=query)

        self.logger.info("Setting Up %s database" % (self.type))

        self.engine = create_engine(self.url, pool_recycle=3600)

        # Catch any errors connecting to database
        try:
            self.engine.connect()
        except OperationalError:
            self.plex_themes.logger.error("OperationalError: Unable to connect to database.")
            raise

        # Create our tables
        BASE.metadata.create_all(self.engine)

        self.ssession = scoped_session(sessionmaker(bind=self.engine))

    def connect(self):
        if self.type != 'sqlite':
            self.plex_themes.logger.warning(
                "Raw connection requested when 'db_type' is not 'sqlite':\n"
                "Consider using 'db.session()' to get a SQLAlchemy session "
                "instead here:\n%s",
                traceback.format_list(traceback.extract_stack()[:-1])[-1][:-1])
        return self.engine.raw_connection()

    def session(self):
        return self.ssession()

    def execute(self, *args, **kwargs):
        return self.engine.execute(*args, **kwargs)

    def get_uri(self):
        return self.url

    """Below functions are for manipulation of data in the database."""

    # Rollar Values

    def set_plex_themes_value(self, item, key, value, namespace='default'):
        """
        Set Rollar value.
        """

        item = item.lower()
        value = json.dumps(value, ensure_ascii=False)
        session = self.ssession()
        try:
            result = session.query(RollarValues) \
                .filter(RollarValues.item == item)\
                .filter(RollarValues.namespace == namespace)\
                .filter(RollarValues.key == key) \
                .one_or_none()
            # ProgramValue exists, update
            if result:
                result.value = value
                session.commit()
            # DNE - Insert
            else:
                new_itemvalue = RollarValues(item=item, namespace=namespace, key=key, value=value)
                session.add(new_itemvalue)
                session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def get_plex_themes_value(self, item, key, namespace='default'):
        """
        Get Rollar value.
        """

        item = item.lower()
        session = self.ssession()
        try:
            result = session.query(RollarValues) \
                .filter(RollarValues.item == item)\
                .filter(RollarValues.namespace == namespace)\
                .filter(RollarValues.key == key) \
                .one_or_none()
            if result is not None:
                result = result.value
            return _deserialize(result)
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def delete_plex_themes_value(self, item, key, namespace='default'):
        """
        Delete Rollar value.
        """

        item = item.lower()
        session = self.ssession()
        try:
            result = session.query(RollarValues) \
                .filter(RollarValues.item == item)\
                .filter(RollarValues.namespace == namespace)\
                .filter(RollarValues.key == key) \
                .one_or_none()
            # ProgramValue exists, delete
            if result:
                session.delete(result)
                session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()
