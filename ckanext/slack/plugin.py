import os
import pdb
import pprint
import ckan.model.package as package
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.slack.model.slack_user as slack_user
from slackclient import SlackClient
from routes.mapper import SubMapper
from sqlalchemy.inspection import inspect

#this will pose an issue, how do we get the id or name here???
#this is probably passing to the config issue
#bot = slack_user.Slack_user().get()
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
BOT_ID = os.environ.get("BOT_ID")
PREVIOUS_OPERATION = None

class SlackPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IMapper)
    plugins.implements(plugins.IRoutes, inherit=True)

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

