from django.db import connections
from django.db import connection
from django.conf import settings


def _get_tables(db_name, db_label=None):
    db_label = db_label or db_name
    _connection = connection if db_label == 'default' else connections[db_label]
    _cursor = _connection.cursor()
    _cursor.execute('show tables;')
    db_tables = tuple(row[0] for row in _cursor.fetchall())
    return db_tables


class _Router(object):
    db_name = None
    db_tables = ()
    app_labels = ()

    def db_for_read(self, model, **hints):
        if (model._meta.db_table in self.db_tables) or (model._meta.app_label in self.app_labels):
            return self.db_name
        return None


class MetaDBRouter(_Router):
    db_name = 'metadb'

    if settings.DATABASES.get(db_name):
        db_tables = _get_tables(db_name, db_label=db_name)

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)


class DjangoRouter(_Router):
    db_name = 'django'

    if settings.DATABASES.get(db_name):
        db_tables = _get_tables(db_name, db_label=db_name)

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)


class CRSdbRouter(_Router):
    db_name = 'CRSdb'
    if settings.DATABASES.get(db_name):
        db_tables = _get_tables(db_name, db_label=db_name)

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)
