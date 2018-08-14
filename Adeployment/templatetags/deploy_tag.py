# -*- coding:utf-8-*-
from django.template import Library
from django.utils.safestring import mark_safe
from container.package.kube import kube_func

register = Library()
@register.simple_tag
def build_project_name(admin_class):
    return admin_class.model._meta.model_name

@register.simple_tag
def build_verbose_name(admin_class):
    return admin_class.model._meta.verbose_name


@register.simple_tag
def get_abs_value(loop_num , curent_page_number):
    return abs(loop_num - curent_page_number)

@register.simple_tag
def build_time(row):

    td = "<td class='text-center'>%s</td>" %row.create_date.strftime("%Y-%m-%d %H:%M:%S")
    return mark_safe(td)

@register.simple_tag
def get_selected_m2m_objects(form_obj,field_name):

    if form_obj.instance.id:
        field_obj = getattr(form_obj.instance, field_name)
        return field_obj.all()
    else:
        return []

@register.simple_tag
def get_m2m_objects(admin_class,field_name,selected_objs):
    field_obj = getattr(admin_class.model,'%s'%field_name)
    all_objects = field_obj.rel.to.objects.all()
    return set(all_objects) - set(selected_objs)