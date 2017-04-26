import datetime
import uuid
import json

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import class_mapper
try:
    from sqlalchemy.engine.result import RowProxy
except:
    from sqlalchemy.engine.base import RowProxy

slack_bot_table = None
slack_bot = None

def make_uuid():
    return unicode(uuid.uuid4())

def init_db(model):
    class _Slack_bot(model.DomainObject):

        @classmethod
        def get(cls, slack_bot_reference):
            query = query.filter(or_(cls.name == slack_bot_reference,
                                     cls.id == slack_bot_reference))
            return query.first()

    global Slack_bot
    Slack_bot = _Slack_bot
    # We will just try to create the table.  If it already exists we get an
    # error but we can just skip it and carry on.
    sql = '''
                CREATE TABLE ckanext_slack_bot (
                    id text NOT NULL PRIMARY KEY,
                    name text NOT NULL,
                    token text,
                    groups integer ARRAY,
                    org text,
                    create_dataset boolean,
                    update_dataset boolean,
                    delete_dataset boolean
                );
    '''
    conn = model.Session.connection()
    try:
        #print(sql)
        conn.execute(sql)
    except sa.exc.ProgrammingError:
        pass

    model.Session.commit()

    sql_upgrade_01 = (
        "ALTER TABLE ckanext_slack_bot add column publish_date timestamp;",
        "ALTER TABLE ckanext_slack_bot add column user_type Text;",
        "UPDATE ckanext_slack_bot set user_type = 'user';",
    )

    conn = model.Session.connection()
    try:
        for statement in sql_upgrade_01:
            conn.execute(statement)
    except sa.exc.ProgrammingError:
        pass
    model.Session.commit()

    sql_upgrade_02 = ('ALTER TABLE ckanext_slack_bot add column extras Text;',
                      "UPDATE ckanext_slack_bot set extras = '{}';")

    conn = model.Session.connection()
    try:
        for statement in sql_upgrade_02:
            conn.execute(statement)
    except sa.exc.ProgrammingError:
        pass
    model.Session.commit()

    types = sa.types
    global slack_bot_table
    slack_bot_table = sa.Table('ckanext_slack_bot', model.meta.metadata,
        sa.Column('id', types.UnicodeText, primary_key=True),
        sa.Column('name', types.UnicodeText, nullable=False),
        sa.Column('token', types.UnicodeText),
        sa.Column('groups', ARRAY(types.Integer)),
        sa.Column('org', types.UnicodeText),
        sa.Column('create_dataset', types.Boolean),
        sa.Column('update_dataset', types.Boolean),
        sa.Column('delete_dataset', types.Boolean),
        extend_existing=True
    )

    model.meta.mapper(
        Slack_bot,
        slack_bot_table,
    )


def table_dictize(obj, context, **kw):
    '''Get any model object and represent it as a dict'''
    result_dict = {}

    if isinstance(obj, RowProxy):
        fields = obj.keys()
    else:
        ModelClass = obj.__class__
        table = class_mapper(ModelClass).mapped_table
        fields = [field.name for field in table.c]

    for field in fields:
        name = field
        if name in ('current', 'expired_timestamp', 'expired_id'):
            continue
        if name == 'continuity_id':
            continue
        value = getattr(obj, name)
        if name == 'extras' and value:
            result_dict.update(json.loads(value))
        elif value is None:
            result_dict[name] = value
        elif isinstance(value, dict):
            result_dict[name] = value
        elif isinstance(value, int):
            result_dict[name] = value
        elif isinstance(value, datetime.datetime):
            result_dict[name] = value.isoformat()
        elif isinstance(value, list):
            result_dict[name] = value
        else:
            result_dict[name] = unicode(value)

    result_dict.update(kw)

    ##HACK For optimisation to get metadata_modified created faster.

    context['metadata_modified'] = max(result_dict.get('revision_timestamp', ''),
                                       context.get('metadata_modified', ''))

    return result_dict