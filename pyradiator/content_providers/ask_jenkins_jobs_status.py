import collections
import datetime
import logging
import re
import time

import requests
import prettytable

from pyradiator.common import ColoredString
from pyradiator.content_providers.ask_x import AskX


LOGGER = logging.getLogger(__name__)

CURRENT_BUILD = 0
LAST_BUILD = 1
COLOR_MAP = {
    "UNSTABLE": (255, 255, 0),
    "FAILURE": (255, 0, 0),
    "SUCCESS": (0, 255, 0),
}
JSON_API_URL = "/api/json"

JenkinsJobs = collections.namedtuple("JenkinsJobs", ["url", "job_names"])


def get_job_info(jenkins_url, job_name):
    LOGGER.debug("Get status of the job %s", job_name)
    job_summary = get_job_summary(jenkins_url, job_name)
    last_build_info = get_build_info(job_summary, LAST_BUILD)
    current_build_info = get_build_info(job_summary, CURRENT_BUILD)
    return (
        get_job_name(job_summary, last_build_info),
        get_job_status(current_build_info),
        get_job_eta(current_build_info)
    )


def get_job_summary(jenkins_url, job_name):
    return requests.get(jenkins_url + job_name + JSON_API_URL).json()


def get_build_info(job_summary, build_number):
    return requests.get(job_summary["builds"][build_number]["url"] + JSON_API_URL).json()


def get_job_name(job_summary, last_build_info):
    color = COLOR_MAP.get(last_build_info["result"], (255, 255, 255))
    return ColoredString(job_summary["name"], color)


def get_current_build_info(job_summary):
    return requests.get(job_summary["builds"][CURRENT_BUILD]["url"] + JSON_API_URL).json()


def get_job_status(build_info):
    if build_info["result"] is None and build_info["building"]:
        return ColoredString("BUILDING", (255, 255, 255))
    else:
        color = COLOR_MAP.get(build_info["result"], (255, 255, 255))
        return ColoredString(build_info["result"], color)


def get_job_eta(job):
    start_time, duration = job["timestamp"], job["estimatedDuration"]
    eta = get_formatted_eta(start_time, duration)
    percent = get_formatted_percent(start_time, duration)
    if job["building"]:
        eta = "{:>8}, {:3}%".format(eta, percent)
    else:
        eta = "N/A"
    return ColoredString(eta, (255, 255, 255))


def get_formatted_eta(start_time, duration):
    now = datetime.datetime.now()
    eta = datetime.datetime.fromtimestamp((start_time + duration) / 1000) - now
    return "N/A" if eta.days < 0 else format_time_delta(eta)


def format_time_delta(time_delta):
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}:{:02}:{:02}".format(hours, minutes, seconds)


def get_formatted_percent(start_time, duration):
    percent = (int(time.time()) - start_time / 1000) * 100 / (duration / 1000)
    return 100 if percent > 100 else percent


class AskJenkinsJobsStatus(AskX):

    COLUMN_1 = "Jenkins Job Name                     "
    COLUMN_2 = " Status "
    COLUMN_3 = "     E.T.A.     "

    def __init__(self, jobs):
        self.jobs = jobs
        self.pretty_table_row_pattern = re.compile(r"(\|\s+)(.*)(\s+\|\s+)(.*)(\s+\|\s+)(.*)(\s+\|)")

    def __call__(self):
        LOGGER.debug("{}.__call__ called".format(self.__class__.__name__))
        table = prettytable.PrettyTable([self.COLUMN_1, self.COLUMN_2, self.COLUMN_3])
        table.align[self.COLUMN_1] = "l"

        try:
            job_info_list = [get_job_info(self.jobs.url, x) for x in self.jobs.job_names]
            for job_info in job_info_list:
                job_info_columns = [x.text for x in job_info]
                table.add_row(job_info_columns)
        except Exception:
            return []

        table_lines = table.get_string().splitlines()
        text = []
        for line in table_lines[:3]:
            text.append([ColoredString(line)])
        for i, line in enumerate(table_lines[3:-1]):
            hit = self.pretty_table_row_pattern.match(line)
            if hit:
                text.append([
                    ColoredString(hit.group(1)),
                    ColoredString(hit.group(2), job_info_list[i][0].color),
                    ColoredString(hit.group(3)),
                    ColoredString(hit.group(4), job_info_list[i][1].color),
                    ColoredString(hit.group(5)),
                    ColoredString(hit.group(6), job_info_list[i][2].color),
                    ColoredString(hit.group(7)),
                ])
        text.append([ColoredString(table_lines[-1])])
        return text
