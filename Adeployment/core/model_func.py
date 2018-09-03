# -*- coding:utf-8-*-


from Adeployment.admin_base import site
from Adeployment.core.environments import get_playbook
from Adeployment.core.logger import *



def save_file(filename,filetype):
    file_path = get_playbook()
    logger("获取文件:%s" %file_path,LOG_LEVEL=logging.INFO,log_type="system")
    now_date = time.strftime('%Y-%m-%d_%H:%M:%S',time.localtime(time.time()))
    try:
        logger("拼接文件路径",LOG_LEVEL=logging.INFO,log_type="system")
        filepath = os.path.join(file_path,filename.name+'-'+now_date).encode('utf-8')
        logger("新的文件路径:%s" %filepath,LOG_LEVEL=logging.INFO,log_type="system")
        f = open(filepath.encode('utf-8'),'w')
        logger("写入文件",LOG_LEVEL=logging.INFO,log_type="system")
        for chunk in filename.chunks():
            f.write(chunk)
        logger("写入文件完成",LOG_LEVEL=logging.INFO,log_type="system")
        logger("关闭文件",LOG_LEVEL=logging.INFO,log_type="system")
        f.close()
        logger("写入数据库",LOG_LEVEL=logging.INFO,log_type="system")
        if Save_to_DB().upfile_to_db(filename,filetype,file_path,now_date):
            logger("写入数据库成功", LOG_LEVEL=logging.INFO, log_type="system")
            return True
    except TypeError as e:
        logger("写入文件错误:%s" %e,LOG_LEVEL=logging.ERROR,log_type="system")
        return False

def delete_file(name):
    if os.path.isfile(name):
        os.remove(name)
    return True


class Save_to_DB(object):
    def __init__(self):
        for app_name in site.registered_admins:
            self.admin_class = site.registered_admins[app_name]

    def upfile_to_db(self,filename,filetype,file_path,now_date):


        files = self.admin_class.get('files')
        files.model.objects.create(file_name=filename.name,
                                   file_path=file_path,
                                   file_type_id=filetype,
                                   create_date=now_date,
                                   )
        return True

    def save_logs_to_db(self,name):
        log_func = self.admin_class.get('logs')
        log_func.model(name=name).save()
        return True

    def read_db(self):
        log_func = self.admin_class.get('deploylist')
        return log_func

    def clear_logs(self):
        admin_class = self.admin_class.get('deploylist')
        admin_class.model.objects.all().delete()
        return True


class Get_DB(Save_to_DB):

    def get_setting(self):
        admin_class = self.admin_class.get('settings')
        return admin_class

    def get_field(self,admin_class, id):
        name = admin_class.model.objects.values('id', 'name').filter(id=id)
        return name[0]['name'].decode('utf-8')

save_db = Save_to_DB()
get_db = Get_DB()