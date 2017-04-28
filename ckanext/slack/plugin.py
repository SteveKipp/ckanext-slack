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

#this will pose an issue, how do we get the id or name here???
#this is probably passing to the config issue
#bot = slack_user.Slack_user().get()
slack_client = None
BOT_ID = None
PREVIOUS_OPERATION = None

def slack_config(id):

    try:
        context = {'for_view': True}
        slack_config_options = slack_user.Slack_user().get(id)
        global slack_client
        slack_client = SlackClient(slack_config_options.token)
        global BOT_ID
        BOT_ID = slack_config_options.bot_id
        form = db.table_dictize(slack_config_options, context)
        jsonform = json.dumps(form)
        return str(jsonform)
    except exc.SQLAlchemyError:
        return 'failure'

group_type = u'grup'
group_type_utf8 = group_type.encode('utf8')

def get_slack_channels():
    channels = slack_client.api_call('channels.list', exclude_archived=1)
    return channels['channels']

class SlackPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IMapper)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)

    # Tell CKAN what custom template helper functions this plugin provides,
    def get_helpers(self):
        return {'slack_config': slack_config,
                'get_slack_channels': get_slack_channels}

    #IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'slack')

    def talk(self, channel, edit_type, id):
        pkg = package.Package().get(id)
        if pkg != None:
            global PREVIOUS_OPERATION
            if pkg.state != 'deleted':
                if edit_type == 'updated' and pkg.state != 'draft' and PREVIOUS_OPERATION != 'created':
                    PREVIOUS_OPERATION = 'updated'
                    msg = "Dataset Notice: The {} dataset has been updated.".format(pkg.title)
                elif edit_type == 'created':
                    PREVIOUS_OPERATION = 'created'
                    msg = "Dataset Notice: The {} dataset has been created.".format(pkg.title)
                elif PREVIOUS_OPERATION == 'created' and pkg.state != 'draft':
                    PREVIOUS_OPERATION = 'updated'
            else:
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

