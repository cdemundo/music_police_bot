# -*- coding: utf-8 -*-
"""
Python Slack Bot class for use with the pythOnBoarding app
"""
import os

from slackclient import SlackClient
from auth_data import AuthData

import bs4
import re
import requests

# To remember which teams have authorized your app and what tokens are
# associated with each team, we can store this information in memory on
# as a global object. When your bot is out of development, it's best to
# save this in a more persistant memory store.
authed_teams = {}

auth_data = AuthData()


class Bot(object):
    """ Instanciates a Bot object to handle Slack onboarding interactions."""
    def __init__(self):
        super(Bot, self).__init__()
        self.name = "music_police_bot"
        self.emoji = ":robot_face:"
        # When we instantiate a new bot object, we can access the app
        # credentials we set earlier in our local development environment.
        self.oauth = {"client_id": auth_data.client_id,
                      "client_secret": auth_data.client_secret,
                      # Scopes provide and limit permissions to what our app
                      # can access. It's important to use the most restricted
                      # scope that your app will need.
                      "scope": "bot"}
        self.verification = auth_data.signing_secret

        # NOTE: Python-slack requires a client connection to generate
        # an oauth token. We can connect to the client without authenticating
        # by passing an empty string as a token and then reinstantiating the
        # client with a valid OAuth token once we have one.
        self.client = SlackClient("")
        # We'll use this dictionary to store the state of each message object.
        # In a production environment you'll likely want to store this more
        # persistantly in  a database.
        self.messages = {}

        #get the token for the bot so we can actually get auth'd to do things
        self.client.token = auth_data.bot_token




    def auth(self, code):
        """
        Authenticate with OAuth and assign correct scopes.
        Save a dictionary of authed team information in memory on the bot
        object.

        Parameters
        ----------
        code : str
            temporary authorization code sent by Slack to be exchanged for an
            OAuth token

        """
        # After the user has authorized this app for use in their Slack team,
        # Slack returns a temporary authorization code that we'll exchange for
        # an OAuth token using the oauth.access endpoint
        auth_response = self.client.api_call(
                                "oauth.access",
                                client_id=self.oauth["client_id"],
                                client_secret=self.oauth["client_secret"],
                                code=code
                                )
        # To keep track of authorized teams and their associated OAuth tokens,
        # we will save the team ID and bot tokens to the global
        # authed_teams object
        team_id = auth_response["team_id"]
        authed_teams[team_id] = {"bot_token":
                                 auth_response["bot"]["bot_access_token"]}
        # Then we'll reconnect to the Slack Client with the correct team's
        # bot token
        self.client = SlackClient(authed_teams[team_id]["bot_token"])

    def no_grateful_dead(self, link, channel):
        """
        Verify if a link includes the grateful dead and post a message warning everyone not to look at it, if so. 

        Parameters
        ----------
        links : list of dicts
            the links associated with the link share event

        """
        #the link has <> surrounding it, lets remove that
        link = re.sub('[<>]', '', link)
        #check if this
        # We want to first check and see if the grateful dead and youtube are mentioned
        res = requests.get(link)
        soup = bs4.BeautifulSoup(res.text, features="html.parser")

        title_tag = soup.select('.watch-title')[0]['title']

        if 'grateful' in title_tag.lower():
            text = "WARNING!! ANDREW IS POSTING GRATEFUL DEAD AGAIN!!"        
            post_message = self.client.api_call(method = "chat.postMessage",
                                                channel=channel,
                                                username=self.name,
                                                icon_emoji=self.emoji,
                                                text=text,
                                                )


   
