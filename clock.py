import subprocess

from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import timezone

schedule = BlockingScheduler(timezone=timezone('Asia/Seoul'))


@schedule.scheduled_job('cron', hour=5)
def daily_job():
    sub_jobs = ['collectpublicdata', 'collectgoogledata', 'collectblogdata', 'analysisdata']
    for job in sub_jobs:
        p = subprocess.Popen('python manage.py {}'.format(job), shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        print(p.communicate())


schedule.start()