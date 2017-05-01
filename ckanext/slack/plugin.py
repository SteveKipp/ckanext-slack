import os
import db
import json
import pprint
import ckan.model.package as package
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.slack.model.slack_user as slack_user
from slackclient import SlackClient
from routes.mapper import SubMapper
from sqlalchemy import exc, inspect
from ckan.common import c

slack_client = None
BOT_ID = None

PREVIOUS_OPERATION = None

def slack_config(id):

    try:
        context = {'for_view': True}
        slack_config_options = slack_user.Slack_user().get(id)

        if slack_config_options != None:
            global slack_client
            global BOT_ID
            slack_client = SlackClient(slack_config_options.token)
            BOT_ID = slack_config_options.bot_id

        form = db.table_dictize(slack_config_options, context)
        json_form = json.dumps(form)
        return str(json_form)
    except exc.SQLAlchemyError:
        return 'failure'

group_type = u'grup'
group_type_utf8 = group_type.encode('utf8')

def get_slack_channels():
    try:
        channels = slack_client.api_call('channels.list', exclude_archived=1)
        return channels['channels']
    except:
        return {}

def get_slack_user_data(id):
    try:
        slack_bot_user =  slack_user.Slack_user().get(id)
        return slack_bot_user
    except:
        return {}

class SlackPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IMapper)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)

    # Tell CKAN what custom template helper functions this plugin provides,
    def get_helpers(self):
        return {'slack_config': slack_config,
                'get_slack_channels': get_slack_channels,
                'get_slack_user_data': get_slack_user_data}

    #IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'slack')

    def get_edit_type(self, p):
        types = []

        if p is not None:
            slack_bot_user = get_slack_user_data(c.userobj.id + "." + p.owner_org)
            if slack_bot_user is not None and slack_bot_user.create_dataset is True:
                types.append('create')
            if slack_bot_user is not None and slack_bot_user.update_dataset is True:
                types.append('update')
            if slack_bot_user is not None and slack_bot_user.delete_dataset is True:
                types.append('delete')

        return types

    def talk(self, channel, edit_type, id):
        pkg = package.Package().get(id)
        if pkg != None:
            slack_user_data = get_slack_user_data(c.userobj.id + "." + pkg.owner_org)

            global slack_client
            if slack_client == None:
                slack_client = SlackClient(slack_user_data.token)

            user_pref = self.get_edit_type(pkg)

            global PREVIOUS_OPERATION
            if pkg.state != 'deleted':
                if edit_type == 'updated' and pkg.state != 'draft' and PREVIOUS_OPERATION != 'created' and 'update' in user_pref:
                    PREVIOUS_OPERATION = 'updated'
                    msg = "Dataset Notice: The {} dataset has been updated.".format(pkg.title)
                elif edit_type == 'created':
                    PREVIOUS_OPERATION = 'created'
                    if 'create' in user_pref:
                        msg = "Dataset Notice: The {} dataset has been created.".format(pkg.title)
                elif PREVIOUS_OPERATION == 'created' and pkg.state != 'draft' and 'update' in user_pref:
                    PREVIOUS_OPERATION = 'updated'
            else:
                if 'delete' in user_pref:
                    PREVIOUS_OPERATION = 'deleted'
                    msg = "Dataset Notice: the {} dataset has been removed.".format(pkg.title)

            try:
                slack_client.api_call("chat.postMessage", channel=channel,
                                       text=msg, as_user=True)
            except:
                pass



    def before_update(self, mapper, connection, instance):
        pass

    def after_update(self, mapper, connection, instance):
        self.talk('general', 'updated', instance.id)


    def before_insert(self, mapper, connection, instance):
        pass

    def after_insert(self, mapper, connection, instance):
        self.talk('general', 'created', instance.id)

    def before_delete(self, mapper, connection, instance):
        pass

    def after_delete(self, mapper, connection, instance):
        pass

    #IRoutes
    def before_map(self, map):
        controller = 'ckanext.slack.controller:SlackController'
        with SubMapper(map, controller=controller) as m:
            m.connect('ckanext_slack_config',
                      '/organization/slack_config/{id}',
                      action='slack_config', ckan_icon='bullhorn', id='{id}')
        return map

