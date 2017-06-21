
import db
import json
import ckan.model.package as package
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.slack.model.slack_user as slack_user
import ckan.lib.helpers as h
from slackclient import SlackClient
from routes.mapper import SubMapper
from ckan.common import c
from pylons import config


slack_client = config['ckan.slackbot_token']
BOT_ID = config['ckan.slackbot_id']

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
    except:
        return 'failure'

group_type = u'grup'
group_type_utf8 = group_type.encode('utf8')

def get_slack_channels():
    try:
        global slack_client
        global BOT_ID
        slack_client = SlackClient(config['ckan.slackbot_token'])
        BOT_ID = config['ckan.slackbot_id']
        private = slack_client.api_call('groups.list', exclude_archived=1)
        public = slack_client.api_call('channels.list', exclude_archived=1)
        channel_objects = private['groups'] + public['channels']
        channel_names = []
        for channel in channel_objects:
            channel_names.append(channel['name'])
        channel_names = sorted(channel_names)
        return channel_names
    except:
        return {}

def get_slack_user_data(id):
        try:
            slack_bot_user = slack_user.Slack_user().get(id)
            return slack_bot_user
        except:
            return {}

def get_slack_config():
    return config


class SlackPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IMapper)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)

    # Tell CKAN what custom template helper functions this plugin provides,
    def get_helpers(self):
        return {'slack_config': slack_config,
                'get_slack_channels': get_slack_channels,
                'get_slack_user_data': get_slack_user_data,
                'get_slack_config': get_slack_config}

    #IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'slack')

    def get_edit_type(self, p):
        types = []

        if p is not None:
            slack_bot_user = get_slack_user_data(c.userobj.id + "." + p.owner_org)
            if slack_bot_user != {}:
                if slack_bot_user is not None and slack_bot_user.create_dataset is True:
                    types.append('create')
                if slack_bot_user is not None and slack_bot_user.update_dataset is True:
                    types.append('update')
                if slack_bot_user is not None and slack_bot_user.delete_dataset is True:
                    types.append('delete')

        return types

    def talk(self, edit_type, id):
        try:
            pkg = package.Package().get(id)
        except:
            pkg = None
            
        if pkg != None and pkg.owner_org is not None:
            url_base = h.get_site_protocol_and_host()
            url = url_base[0]+ '://' + url_base[1] + toolkit.url_for(controller='package', action='read', id=pkg.name)
            slack_user_data = get_slack_user_data(c.userobj.id + "." + pkg.owner_org)
            if slack_user_data != None:
                print("we in here")
                global slack_client
                if slack_client == None:
                    slack_client = SlackClient(slack_user_data.token)

                user_pref = self.get_edit_type(pkg)

                global PREVIOUS_OPERATION
                if pkg.state != 'deleted':
                    if edit_type == 'updated' and pkg.state != 'draft' and PREVIOUS_OPERATION != 'created' and 'update' in user_pref and pkg.private is not True:
                        PREVIOUS_OPERATION = 'updated'
                        msg = "Dataset Notice: The {} dataset has been updated. Link here: {}".format(pkg.title, url)
                    elif edit_type == 'created' and pkg.private is not True:
                        PREVIOUS_OPERATION = 'created'
                        if 'create' in user_pref and pkg.private is not True:
                            msg = "Dataset Notice: The {} dataset has been created. Link here: {}".format(pkg.title, url)
                    elif PREVIOUS_OPERATION == 'created' and pkg.state != 'draft' and 'update' in user_pref:
                        PREVIOUS_OPERATION = 'updated'
                else:
                    if 'delete' in user_pref and pkg.private is not True:
                        PREVIOUS_OPERATION = 'deleted'
                        #do we want to put a link here?
                        msg = "Dataset Notice: the {} dataset has been removed.".format(pkg.title)

                try:
                    for group in slack_user_data.groups:
                        print("talking")
                        print(msg)
                        print(group)
                        print(slack_client)

                        res = slack_client.api_call("chat.postMessage", channel=group,
                                              text=msg, as_user=True)
                        print(res)
                except:
                    pass
        print("this has completed")


    def before_update(self, mapper, connection, instance):
        pass

    def after_update(self, mapper, connection, instance):
        self.talk('updated', instance.id)


    def before_insert(self, mapper, connection, instance):
        pass

    def after_insert(self, mapper, connection, instance):
        self.talk('created', instance.id)

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
                      action='slack_config', ckan_icon='fa fa-slack', id='{id}')
        return map

