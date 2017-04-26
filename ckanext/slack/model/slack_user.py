import ckan.model.domain_object as domain_object
import ckan.model.meta as meta
import ckan.model as model
from sqlalchemy.sql.expression import or_
from sqlalchemy import types, Column, Table
from sqlalchemy.dialects.postgresql import ARRAY

def make_uuid():
    return unicode(uuid.uuid4())

slack_user_table = Table('ckanext_slack_user', model.meta.metadata,
         Column('id', types.UnicodeText, primary_key=True),
         Column('name', types.UnicodeText, nullable=False),
         Column('token', types.UnicodeText),
         Column('groups', ARRAY(types.Integer)),
         Column('org', types.UnicodeText),
         Column('create_dataset', types.Boolean),
         Column('update_dataset', types.Boolean),
         Column('delete_dataset', types.Boolean),
)

class Slack_user(domain_object.DomainObject):

    @classmethod
    def get(cls, slack_user_reference):
        query = meta.Session.query(cls).autoflush(False)
        query = query.filter(or_(cls.id == slack_user_reference_user_reference))
        return query.first()


meta.mapper(slack_user, slack_user_table)