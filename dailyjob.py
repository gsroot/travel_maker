#!/usr/bin/env python
import subprocess

from config.settings.base import ROOT_DIR


def daily_job():
    manage_path = ROOT_DIR.path('manage.py')
    sub_jobs = ['collectpublicdata', 'collectgoogledata', 'collectblogdata', 'analysisdata']
    for job in sub_jobs:
        p = subprocess.Popen('python {} {}'.format(manage_path, job), shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        print(p.communicate())


if __name__ == '__main__':
    daily_job()
