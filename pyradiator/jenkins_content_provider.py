import collections
import datetime
import re
import time

import requests
import prettytable

from common import ColoredString

JSON_API_URL = "/api/json"

JenkinsJobs = collections.namedtuple("JenkinsJobs", ["url", "job_names"])


def get_job_info(jenkins_url, job_name):
    job_summary = get_job_summary(jenkins_url, job_name)
    job_info = get_last_job_info(job_summary)
    return (
        job_summary["name"],
        get_job_status(job_info),
        get_job_eta(job_info)
    )


def get_job_summary(jenkins_url, job_name):
    return requests.get(jenkins_url + job_name + JSON_API_URL).json()


def get_last_job_info(job_summary):
    return requests.get(job_summary["builds"][0]["url"] + JSON_API_URL).json()


def get_job_status(job_info):
    if job_info["result"] is None and job_info["building"]:
        return "BUILDING"
    else:
        return job_info["result"],


def get_job_eta(job):
    start_time, duration = job["timestamp"], job["estimatedDuration"]
    eta = get_formatted_eta(start_time, duration)
    percent = get_formatted_percent(start_time, duration)
    if job["building"]:
        return "{:>8}, {:3}%".format(eta, percent)
    else:
        return "N/A"


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


class AskJenkinsJobStatus(object):

    COLUMN_1 = "Jenkins Job Name                     "
    COLUMN_2 = " Status "
    COLUMN_3 = "     E.T.A.     "

    def __init__(self, jobs):
        self.jobs = jobs
        self.success_pattern = re.compile("(.*)(SUCCESS)(.*)")
        self.failure_pattern = re.compile("(.*)(FAILURE)(.*)")
        self.unstable_pattern = re.compile("(.*)(UNSTABLE)(.*)")
        self.building_pattern = re.compile("(.*)(BUILDING)(.*)")
        self.table = prettytable.PrettyTable([
            self.COLUMN_1,
            self.COLUMN_2,
            self.COLUMN_3
        ])
        self.table.align[self.COLUMN_1] = "l"

    def __call__(self):
        self.table.clear_rows()
        try:
            for job_name in self.jobs.job_names:
                self.table.add_row(get_job_info(self.jobs.url, job_name))
        except Exception:
            return []

        text = []
        for line in self.table.get_string().splitlines():
            hit = self.success_pattern.match(line)
            if hit:
                text.append([ColoredString(hit.group(1)),
                             ColoredString(hit.group(2), (0, 255, 0)),
                             ColoredString(hit.group(3))])
                continue
            hit = self.failure_pattern.match(line)
            if hit:
                text.append([ColoredString(hit.group(1)),
                             ColoredString(hit.group(2), (255, 0, 0)),
                             ColoredString(hit.group(3))])
                continue
            hit = self.unstable_pattern.match(line)
            if hit:
                text.append([ColoredString(hit.group(1)),
                             ColoredString(hit.group(2), (255, 255, 0)),
                             ColoredString(hit.group(3))])
                continue
            hit = self.building_pattern.match(line)
            if hit:
                text.append([ColoredString(hit.group(1)),
                             ColoredString(hit.group(2), (90, 160, 240)),
                             ColoredString(hit.group(3))])
                continue
            text.append([ColoredString(line)])
        return text
