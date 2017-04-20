import os
import pdb

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from slackclient import SlackClient

BOT_NAME = 'ckan_bot'
print(os.environ.get('SLACK_BOT_TOKEN'))
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

class SlackPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IMapper)
    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'slack')

    def before_update(self, mapper, connection, instance):
        pass

    def after_update(self, mapper, connection, instance):
        #pdb.set_trace()
        print("this has run")
        api_call = slack_client.api_call('users.list')
        if api_call.get('ok'):
            users = api_call.get('members')
            for user in users:
                if 'name' in user and user.get('name') == BOT_NAME:
                    print('bot_id found {}:{}'.format(user['name'], user.get('id')))
        else:
            print('could not find that bot')


    def before_insert(self, mapper, connection, instance):
        pass

    def after_insert(self, mapper, connection, instance):
        pass

    def before_delete(self, mapper, connection, instance):
        pass

    def after_delete(self, mapper, connection, instance):
        pass



