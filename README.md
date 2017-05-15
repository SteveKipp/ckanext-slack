# ckanext-slack
This extension provides an simple interface for integrating slack with CKAN.

Works for ckan>=2.5

## Installation

Use `pip` to install this plugin.

underneath the synced_folders/src directory, run:

```
pip install -e 'git+https://github.com/merkelct/ckanext-slack.git#egg=ckanext-slack'
```

## Configuration

Make sure to add both `slackbot_token` and `slackbot_id` in your config file, using your slackbot OAuth token for
slackbot_token and a useful identifier for slackbot_id (as this is what will show up in the actual channel):

```
{
    "slackbot_token":"xoxb-XXXXXXXXXX-XXXXXXXXXXXXXXXXX",
    "slackbot_id": "CKAN Bot"
}
```
The slack bot oauth token can be found in the slack app settings web interface (Under OAuth & Permissions).
Be sure to use the Bot User OAuth Access Token

## Helper Functions

custom helpers available to the templates

```
get_slack_channels() - returns the slack channels that the bot has access to
get_slack_config() - returns the slack configuration generated from the .ini
get_slack_user_data() - returns the slack data for a given user

```

all helpers will be available as h.<helper name>(<vars>)


## Usage

While you can use the slack bot to post to slack using the social snippet, before you can set automatic updates the
bot needs to be configured at

Organization/slack_config/<your organization>

(if not already populated)
1. Enter the Token (Bot User OAuth Access Token)
2. Enter the Bot ID (this can be either the bot name as shown in slack or the actual bot ID
3. Hit update (this will populate the channels)
4. Select any combination of create, update, and delete *
5. Hit update config and you will receive a flash notification if it succeeded or failed


*Create will tell you when a dataset has been created, Update when a dataset has been modified, and delete when a
Dataset has been removed)


Dependencies
------------

* slackclient 1.0.5
