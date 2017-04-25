import os
import pdb
import pprint
import ckan.model.package as package
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from slackclient import SlackClient
from sqlalchemy.inspection import inspect

BOT_NAME = 'ckan_bot'
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

BOT_ID = os.environ.get("BOT_ID")
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"
PREVIOUS_OPERATION = None
print('previous package id loaded')

class SlackPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IMapper)
    # IConfigurer


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



