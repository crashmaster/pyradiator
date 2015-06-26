import getpass
import json
import urllib

import prettytable
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


def gerrit_response_to_pretty_table(response):
    column_1 = "Created"
    column_2 = "Owner"
    column_3 = "Subject"
    table = prettytable.PrettyTable([column_1, column_2, column_3])
    table.align[column_1] = "l"
    table.align[column_2] = "l"
    table.align[column_3] = "l"
    table.sortby = column_1

    for line in response:
        table.add_row([
            line[column_1.lower()][:-6],
            line[column_2.lower()]["name"],
            line[column_3.lower()]
        ])

    return table


class AskGerritOpenChanges(object):

    def __init__(self, gerrit_url, project, team):
        self.query_url = get_gerrit_query_url(gerrit_url, project, team)
        self.authenticator = get_gerrit_authenticator()

    def __call__(self):
        json_response = requests.get(self.query_url, auth=self.authenticator, verify=True)
        response = json.loads(json_response.text[4:])

        return [
            [ColoredString(x)]
            for x in gerrit_response_to_pretty_table(response).get_string().splitlines()
        ]
