import os
import pdb

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from slackclient import SlackClient

BOT_NAME = 'ckan_bot'
print(os.environ.get('SLACK_BOT_TOKEN'))
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# starterbot's ID as an environment variable
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

    def talk(self, channel):
        """
            Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            returns back what it needs for clarification.
        """
        msg = "Hi, good news! and update to a dataset has been made!"
        slack_client.api_call("chat.postMessage", channel=channel,
                              text=msg, as_user=True)

    def before_update(self, mapper, connection, instance):
        pass

    def after_update(self, mapper, connection, instance):
        #pdb.set_trace()
        print("this has run")
        self.talk('general')



    def before_insert(self, mapper, connection, instance):
        pass

    def after_insert(self, mapper, connection, instance):
        pass

    def before_delete(self, mapper, connection, instance):
        pass

    def after_delete(self, mapper, connection, instance):
        pass



