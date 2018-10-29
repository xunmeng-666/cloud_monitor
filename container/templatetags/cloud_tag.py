from django.template import Library
from django.utils.safestring import mark_safe
from container.package.kube import kube_func


register = Library()

@register.simple_tag
def build_node_info(node_info,nodes):
    rle_th = "<th ><a href='/cluster/nodes/node_info/{node}/'>{name}</a></th>".format(node=node_info.metadata.name,name=node_info.metadata.name)
    if "node-role.kubernetes.io/master" in node_info.metadata.labels:
        rle_th += "<th >Master</th>"
    elif "node-role.kubernetes.io/compute" in node_info.metadata.labels:
        rle_th += "<th >Node</th>"
    else:
        rle_th += "<th>OS</th>"

    for status in node_info.status.conditions:
        if status.type == 'Ready' and status.status == 'True':
            rle_th += "<th style='color: #34A637;'>Ready</th>"
        elif status.type == 'Ready' and status.status == 'Unknown':
            rle_th += "<th style='color: #FF0512;'>NotReady</th>"

    for ip_add in node_info.status.addresses:
        if ip_add.type == "InternalIP":
            rle_th += "<th>%s</th>" %ip_add.address
    rle_th += "<th>%s</th>" %node_info.status.allocatable.get('cpu')
    rle_th += "<th>%s</th>" %node_info.status.capacity.get('cpu')
    rle_th += "<th>%sGi</th>" %(round(int(node_info.status.allocatable.get('memory').split('K')[0]) / 1000 /1000 ,2))
    rle_th += "<th>%sGi</th>" %(round(int(node_info.status.capacity.get('memory').split('K')[0]) / 1000 / 1000 ,2))
    rle_th += "<th>%s</th>" %node_info.metadata.creation_timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return mark_safe(rle_th)

@register.simple_tag
def build_node_images(node_func):
    ele = ""
    for name_list in node_func.status.images:

        ele += "<dd style='line-height: 25px'>%s</dd>" %name_list.names[1]
    return mark_safe(ele)

@register.simple_tag
def build_project_name():
    ns = []
    ele = ""
    pods_list = kube_func.get_list_namespace()
    for name in pods_list.items:
        if name.metadata.name not in ns:
            ns.append(name.metadata.name)
    for i in ns:
        # ele += "<option label='%s' value='%s'></option>" %(i,i)
        ele += "<option>"
        ele += "<a href='/cluster/pods/?projects=%s'>"%i+i+"</a>"
        ele += "</option>"
    return mark_safe(ele)

@register.simple_tag
def build_role_kind(namespace_info):
    ns = []
    ele = ""
    for kev,value in namespace_info.items():
        if value['login_user']['kind'] not in ns:
            ns.append(value['login_user']['kind'])
    for i in ns:
        ele += "<option label='%s' value='%s'></option>" %(i,i)
    return mark_safe(ele)


@register.simple_tag
def build_volume_info(pods_info):

    ele = ""
    for volume_info in pods_info.spec.volumes:
        ele += "<h5>%s</h5>" % volume_info.name
        for k,v in volume_info.to_dict().items():
            if v != None and k != 'name':
                ele += "<dt style='text-align: left'>Type:</dt>"
                ele += "<dd>%s</dd>" %k
                for key,valume in v.items():
                    ele += "<dt style='text-align: left'>%s</dt>" %key
                    if valume is None:
                        ele += "<dd>node's default</dd>"
                    else:
                        ele += "<dd>%s</dd>" %valume

    return mark_safe(ele)

@register.simple_tag
def build_role_list():
    ele = ""
    role_list = kube_func.get_all_user_list()
    for name in role_list:
        ele += "<option label='%s' value='%s'></option>" % (name, name)
    return mark_safe(ele)

@register.simple_tag
def build_namespace_list_on_role(objects):
    ro_dict = {k2: v2 for k, v in objects.items() for k1 in v[0]['namespace'] for k2, v2 in k1.items()}
    ele = ""
    for key,value in objects.items():
        for key1,value1 in ro_dict.items():
            ele_tr = "<tr>"
            ele_td = "<td>"+"<a href=/cluster/pods/?project="+key1+">"+key1+"</a>"+"</td>"
            ele_td += "<td>" + value[0]['provider_name'] +"</td>"
            ele_td += "<td>" + str(value1['pod_count']) +"</td>"
            ele_td += "<td>" + value1['login_user']['create_date']+"</td>"
            ele_tr += ele_td
            ele_tr += "</tr>"
            ele += ele_tr
    return mark_safe(ele)