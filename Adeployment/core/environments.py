# -*- coding:utf-8-*-

import os
from Adeployment.conf.conf import *

def get_playbook():
    playbook_path = os.environ.get('PLAYBOOK_PATH')
    if not playbook_path or playbook_path is None:
        playbook_path = FILE_PATH
    return playbook_path

def get_logpath():
    log_path = os.environ.get("LOG_PATH")
    if not log_path or log_path is None:

        if os.path.isdir('/var/log/cloud_monitor/'):pass
        else:
            os.makedirs('/var/log/cloud_monitor/')
        log_path = LOGS_INFO
    return log_path