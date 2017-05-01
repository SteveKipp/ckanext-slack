import ckan.model.meta as meta
import ckanext.slack.model.slack_user as slack_user
from sqlalchemy import exc




def slack_bot_update(slack_bot):
    session = meta.Session
    if slack_user.Slack_user().get(slack_bot['id']) == None:
        s = slack_user.Slack_user()
        s.id = slack_bot['id']
        s.bot_id = slack_bot['bot_id']
        s.token = slack_bot['token']
        groups = [slack_bot['groups']]
        s.groups = groups
        s.org = slack_bot['org']
        s.create_dataset = slack_bot['create_dataset']
        s.update_dataset = slack_bot['update_dataset']
        s.delete_dataset = slack_bot['delete_dataset']
        session.add(s)
    else:
        s = slack_user.Slack_user().get(slack_bot['id'])
        s.id = slack_bot['id']
        s.bot_id = slack_bot['bot_id']
        s.token = slack_bot['token']
        groups = [slack_bot['groups']]
        s.groups = groups
        s.org = slack_bot['org']
        s.create_dataset = slack_bot['create_dataset']
        s.update_dataset = slack_bot['update_dataset']
        s.delete_dataset = slack_bot['delete_dataset']
        session.add(s)
    try:
        session.commit()
        return 'success'
    except exc.SQLAlchemyError:
        session.rollback()
        return 'failure'