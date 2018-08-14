# -*- coding:utf-8-*-
#!/usr/local/bin/python


import os
import json
import logging
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase
from ansible.errors import AnsibleParserError
from Adeployment.core.environments import get_playbook
from Adeployment.core.model_func import save_db
from Adeployment.core.logger import logger_run,logger
from Adeployment.core.rabbitmqs import rabbit_producer


class AnsibleTaskResultCallback(CallbackBase):
    def __init__(self,*args):
        super(AnsibleTaskResultCallback,self).__init__(*args)
        self.ok = json.dumps({})
        self.fail = json.dumps({})
        self.unreachable = json.dumps({})
        self.playbook = ""
        self.no_host = False
        self.fails = []

    def v2_runner_on_ok(self, result):
        host = result._host.get_name()
        self.runner_on_ok(host,result._result)
        data = json.dumps({host:result._result},indent=4)
        self.ok = data
        logger(LOG_INFO = "ok %s"%host,LOG_LEVEL=logging.INFO)
        logger_run(LOG_INFO = "ok %s"%host,LOG_LEVEL=logging.INFO)
        rabbit_producer("ok %s" %host)


    def v2_runner_on_failed(self, result, ignore_errors=False):
        #执行失败的playbook日志
        host = result._host.get_name()
        self.runner_on_failed(host,result._result,ignore_errors)
        data = json.dumps({host:result._result},indent=4)
        self.fail = data
        logger(LOG_INFO = 'Run Fails：%s' %host,LOG_LEVEL=logging.ERROR)
        logger_run(LOG_INFO = 'Run Fails：%s' %host,LOG_LEVEL=logging.ERROR)
        self.fails.append(['Run Fails：%s' %data])


    def v2_runner_on_unreachable(self, result):
        #未能连接到playbook的日志
        host = result._host.get_name()
        self.runner_on_unreachable(host,result._result)
        data = json.dumps({host:result._result},indent=4)
        self.unreachable = data
        self.fails.append('Connect to host fails: %s' %self.unreachable)
        logger(LOG_INFO='Connect to host fails: %s' %self.unreachable,LOG_LEVEL=logging.INFO)
        logger_run(LOG_INFO='Connect to host fails: %s' %self.unreachable,LOG_LEVEL=logging.INFO)
        rabbit_producer('Connect to host fails: %s' %self.unreachable)

    def v2_playbook_on_play_start(self, play):
        #记录正在执行的playbook
        self.playbook_on_play_start(play.name)
        self.playbook = play.name
        logger(LOG_INFO='Run Model :%s' %self.playbook,LOG_LEVEL=logging.INFO)
        logger_run(LOG_INFO='Run Model :%s' %self.playbook,LOG_LEVEL=logging.INFO)
        rabbit_producer('Run Model :%s' % self.playbook)


    def v2_playbook_on_task_start(self, task, is_conditional):

        logger(LOG_INFO=task,LOG_LEVEL=logging.INFO)
        logger_run(LOG_INFO=task,LOG_LEVEL=logging.INFO)
        rabbit_producer("%s" %task)


    def v2_playbook_on_stats(self, stats):
        hosts = sorted(stats.processed.keys())
        summary = {}
        info = []
        for h in hosts:
            s = stats.summarize(h)
            summary[h] = s
        for i in summary:
            ok = "ok=%s".encode('utf-8') % (summary.get(i).get('ok'))
            changed = "changed=%s" % (summary.get(i).get("changed"))
            unreachable = "unreachable=%s" % (summary.get(i).get("unreachable"))
            failed = "failed=%s" % (summary.get(i).get("failures"))
            skipped = "skipped=%s" % (summary.get(i).get('skipped'))
            info.append([i, ok, changed, unreachable, failed, skipped])

        logger('运行结果:',logging.INFO)
        logger_run('运行结果:',logging.INFO)

        for infos in info:
            rabbit_producer("%s" % infos)
            logger("%s"%infos,logging.INFO)
            logger_run("%s"%infos,logging.INFO)
        rabbit_producer('Error info')
        logger('错误信息', logging.INFO)
        logger_run('错误信息', logging.INFO)

        for infos in self.fails:
            if infos in self.fails:
                rabbit_producer("%s" %infos)
                logger(LOG_INFO='%s' % infos, LOG_LEVEL=logging.INFO)
                logger_run(LOG_INFO='%s' % infos, LOG_LEVEL=logging.INFO)
            else:
                logger("没有错误信息",logging.INFO)
                logger_run("没有错误信息",logging.INFO)

        save_db.save_logs_to_db()

        rabbit_producer("quit")
    def v2_playbook_on_no_hosts_matched(self):
        #未能匹配到任何playbook， 不执行任何操作
        self.playbook_on_no_hosts_matched()
        self.no_host = True
        logger(LOG_INFO= "No_Host:%s" %self.no_host,LOG_LEVEL= logging.WARNING)
        logger_run(LOG_INFO= "No_Host:%s" %self.no_host,LOG_LEVEL= logging.WARNING)

class AnsibleTask:
    def __init__(self, hosts_list, extra_vars=None):
        self.hosts_file = hosts_list
        Options = namedtuple('Options',
                             ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check',
                              'diff', 'host_key_checking', 'listhosts', 'listtasks', 'listtags', 'syntax'])

        self.options = Options(connection='ssh', module_path=None, forks=10,
                               become=None, become_method=None, become_user=None, check=False, diff=False,
                               host_key_checking=False, listhosts=None, listtasks=None, listtags=None, syntax=None)
        self.loader = DataLoader()
        self.passwords = dict(vault_pass='secret')

        self.inventory = InventoryManager(loader=self.loader, sources=[self.hosts_file])
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)
        if extra_vars:
            self.variable_manager.extra_vars = extra_vars


    def exec_playbook(self, playbooks):
        if not os.path.exists(playbooks[0]):
            code = 1000
            complex = {"playbook":playbooks,'msg':playbooks +"playbook does not exist",'flag':False}
            simple = 'playbook does not exist about' + playbooks
            return code,complex,simple
        results_callback = AnsibleTaskResultCallback()
        playbook = PlaybookExecutor(playbooks=playbooks, inventory=self.inventory,
                                    variable_manager=self.variable_manager,
                                    loader=self.loader, options=self.options, passwords=self.passwords)
        setattr(getattr(playbook, '_tqm'), '_stdout_callback', results_callback)
        try:
            playbook.run()
        except AnsibleParserError as e:
            logger(LOG_INFO='Error: %s' %e,LOG_LEVEL= logging.ERROR)
            rabbit_producer('Error: %s' %e)


def run_ansi(playbook,inventory):
    task = AnsibleTask(hosts_list=inventory)
    task.exec_playbook([playbook])

def build_file(inven_func,playb_func,admin_class):
    inventoryfile = join_host_file(inven_func,admin_class)
    playbook_env = join_playbook_file(playb_func,admin_class)
    run_ansi(playbook=playbook_env,inventory=inventoryfile)


def join_playbook_file(playb_func,admin_class):
    playbook_name = admin_class.model.objects.get(id=playb_func).file_name
    playbook_date = admin_class.model.objects.get(id=playb_func).create_date.strftime("%Y-%m-%d_%H:%M:%S")
    playbook = "%s%s-%s" % (get_playbook(), playbook_name, playbook_date)
    return playbook.encode('utf-8')

def join_host_file(inven_func,admin_class):

    inventory_name = admin_class.model.objects.get(id=inven_func).file_name
    # inventory_path = admin_class.model.objects.get(id=inven_func).file_path
    inventory_date = admin_class.model.objects.get(id=inven_func).create_date.strftime("%Y-%m-%d_%H:%M:%S")
    inventoryfile = "%s%s-%s" % (get_playbook(), inventory_name, inventory_date)
    return inventoryfile.encode('utf-8')