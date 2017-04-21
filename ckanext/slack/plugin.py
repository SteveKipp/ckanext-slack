import os
import pdb
import ckan.model as model
import pylons
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from slackclient import SlackClient

BOT_NAME = 'ckan_bot'
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

BOT_ID = os.environ.get("BOT_ID")
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

class SlackPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IMapper)
    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'slack')

    def talk(self, channel, update_type, pkg):
        msg = "Hi, good news! The {} dataset has been {}!".format(pkg['title'], update_type)
        slack_client.api_call("chat.postMessage", channel=channel,
                              text=msg, as_user=True)

    def before_update(self, mapper, connection, instance):
        pass

    def after_update(self, mapper, connection, instance):
        data_dict={'id':instance.id}
        context = {'model': model, 'session': model.Session,
                   'user': pylons.c.user}
        pkg = toolkit.get_action('package_show')(context, data_dict)
        self.talk('general', 'updated', pkg)



    def before_insert(self, mapper, connection, instance):
        pass

    def after_insert(self, mapper, connection, instance):
        pass

    def before_delete(self, mapper, connection, instance):
        pass

    def after_delete(self, mapper, connection, instance):
        pass



