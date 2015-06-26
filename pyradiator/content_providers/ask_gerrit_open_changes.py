import getpass
import json
import urllib

import requests

from pyradiator.common import ColoredString


def get_gerrit_authenticator():
    user = raw_input("User: ")
    password = getpass.getpass()
    return requests.auth.HTTPBasicAuth(user, password)


def get_gerrit_query_url(gerrit_url, project, team):
    address = get_gerrit_address(gerrit_url)
    query = get_gerrit_query(project, team)
    return "{}{}".format(address, urllib.quote(query))


def get_gerrit_address(gerrit_url):
    return "https://{}/a/changes/?q=".format(gerrit_url)


def get_gerrit_query(project, team):
    project = "project:{}".format(project)
    status = "status:{}".format("open")
    ower_in = "ownerin:{}".format(team)
    return " AND ".join([project, status, ower_in])


class AskGerritOpenChanges(object):

    def __init__(self, gerrit_url, project, team):
        self.query_url = get_gerrit_query_url(gerrit_url, project, team)
        self.authenticator = get_gerrit_authenticator()

    def __call__(self):
        response = requests.get(self.query_url, auth=self.authenticator, verify=True)
        json_response = json.loads(response.text[4:])
        print json_response
        return [[ColoredString("text", (255, 255, 50))]]
