#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) 2019, Thilo Wening <thilo.wening@netways.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '0.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
module: icinga2_objects_generator
short_description: Generate Strings of Icinga 2 Objects
description: This module generates strings of icinga2 objects to use in configuration.
author: Thilo Wening (@mkayontour)
options:
  name:
    description: Name of the host object
    required: true
    type: string
  state:
    description: |
      Choose between present or absent,
      whether the host should be created or deleted
    required: true
    type: string
'''

EXAMPLES = r'''
# Create Host
- name: Create Host at Director
  icinga2_director_host:
    name: agent.localdomain
    host: "http://icingaweb.localdomain/icingaweb2"
    username: 'icinga'
    password: 'icinga'
    state: 'present'
    templates:
      - "basic-host"
    host_vars:
      address: "127.0.0.1"
      check_interval: "300"
      check_command: "hostalive"
    custom_vars:
      os: "Linux"
      application: "Apache"
'''

RETURN = r'''
 test blubber
'''

from ansible.module_utils.basic import AnsibleModule
from icinga2_attributes import i2_lookup
import re





# res = dict(changed=True, ansible_module_results="created new host object", return_code=c.status_code)
# module.fail_json(msg=("Failed to update host, maybe the hostgroup or a template is not available: "
#                                           + str(r.status_code) + str(r.text)))


class Icinga2Objects(object):

    def __init__(self):
        self.vars={}
        self.attrs={}
        self.object_type = module.params.get('object_type')
        self.object_name = module.params.get('object_name')
        self.state = module.params.get('state')
        self.imports = module.params.get('imports')
        self.vars['vars'] = module.params.get('vars')
        self.attrs = module.params.get('attrs')
        self.assign = module.params.get('assign')
        self.apply = module.params.get('apply')
        self.apply_target = module.params.get('apply_target')

        if re.match(r'^(Service|Notification|Dependency)$', self.object_type) and self.state == 'apply':
            if re.match(r'^(Notification|Dependency)$', self.object_type) and not (self.apply_target and self.assign):
                module.fail_json(msg=("Notifications or Dependencies need a apply_target and assign rules."))
            elif self.object_type == "Service" and not self.assign:
                module.fail_json(msg=("Apply Service need assign rules."))







        #print(self.attrs)
        if self.attrs:
          Icinga2Objects.check_attrs(attrs=self.attrs, object_type=self.object_type)

    def check_attrs(attrs, object_type):
        object_attrs = {}
        object_attrs['ApiUser']={
                'password':'str',
                'permissions':'list',
                'client_cn':'str'
        }
        object_attrs['CheckCommand']={
            'command':'list',
            'env':'dict',
            'vars':'dict',
            'timeout':'str',
            'arguments':'dict'
        }
        object_attrs['Host']={
            'display_name':'str',
            'address':'str',
            'address6':'str',
            'groups':'list',
            'check_command':'str',
            'max_check_attempts':'int',
            'check_period':'str',
            'check_timeout':'str',
            'check_interval':'str',
            'retry_interval': 'str',
            'enable_notifications':'bool',
            'enable_active_checks':'bool',
            'enable_passive_checks':'bool',
            'enable_event_handler':'bool',
            'enable_flapping':'bool',
            'enable_perfdata':'bool',
            'event_command':'str',
            'flapping_threshold_high':'int',
            'flapping_threshold_low':'int',
            'volatile':'bool',
            'zone':'str',
            'command_endpoint':'str',
            'notes':'str',
            'notes_url':'str',
            'action_url':'str',
            'icon_image':'str',
            'icon_image_alt':'str'
        }

        object_attrs['HostGroup']={
            'display_name':'str',
            'groups':'list'
        }

        object_attrs['Dependency']={
            'parent_host_name':'str',
            'parent_service_name':'str',
            'child_host_name':'str',
            'child_service_name':'str',
            'disable_checks':'bool',
            'disable_notifications':'bool',
            'ignore_soft_states':'bool',
            'period':'str',
            # Maybe I would check if states are set right
            #'states':['OK','Warning','Critical','Unknown','Up','Down']
            'states':'list'
        }

        object_attrs['Endpoint']={
            'host':'str',
            'port':'int',
            'log_duration':'str'
        }

        object_attrs['EventCommand']={
            'command':'list',
            'env':'dict',
            'timeout':'str',
            'arguments':'str'
        }

        object_attrs['Notification']={
            'host_name':'str',
            'service_name':'str',
            'users':'list',
            'user_groups':'list',
            'times':'dict',
            'command':'str',
            'interval':'str',
            'period':'str',
            'zone':'str',
            'types':'list',
            'states':'list'
        }

        object_attrs['NotificationCommand']={
            'command':'list',
            'env':'dict',
            'timeout':'str',
            'arguments':'dict'
        }

        object_attrs['ScheduledDowntime']={
            'host_name':'str',
            'service_name':'str',
            'author':'str',
            'comment':'str',
            'fixed':'bool',
            'duration':'str',
            'ranges':'dict',
            'child_options':'str'
        }

        object_attrs['Service']={
            'display_name': 'str',
            'host_name':'str',
            'groups': 'list',
            'check_command': 'str',
            'max_check_attempts': 'int',
            'check_period': 'str',
            'check_timeout': 'str',
            'check_interval': 'str',
            'retry_interval': 'str',
            'enable_notifications': 'bool',
            'enable_active_checks': 'bool',
            'enable_passive_checks': 'bool',
            'enable_event_handler': 'bool',
            'enable_flapping': 'bool',
            'enable_perfdata': 'bool',
            'event_command': 'str',
            'flapping_threshold_high': 'int',
            'flapping_threshold_low': 'int',
            'volatile': 'bool',
            'zone': 'str',
            'name':'str',
            'command_endpoint': 'str',
            'notes': 'str',
            'notes_url': 'str',
            'action_url': 'str',
            'icon_image': 'str',
            'icon_image_alt': 'str'
        }

        if not object_type in object_attrs.keys():
            module.fail_json(msg=object_type + " not yet supported.")

        for attr,value in attrs.items():
            #print("attr=" + attr)
            #print(value)
            if attr in object_attrs[object_type]:
                attr_type=object_attrs[object_type][attr]
                #print(type(value), attr_type)
                #print(value)
                if attr_type == 'str' and not isinstance(value, str):
                    module.fail_json(msg=("Attribute " + attr + " should be a string. Check your Vars!"))
                elif attr_type == 'list' and not isinstance(value, list):
                    module.fail_json(msg=("Attribute " + attr + " should be a Array. Check your Vars!"))
                elif attr_type == 'dict' and not isinstance(value, dict):
                    module.fail_json(msg=("Attribute " + attr + " should be a Dictionary. Check your Vars!"))
                elif attr_type == 'bool' and not re.match(r'^(true|false)$', value):
                    module.fail_json(msg=("Attribute " + attr + " should be a boolean. Check your Vars!"))
                elif attr_type == 'int' and not isinstance(value, int):
                    module.fail_json(msg=("Attribute " + attr + " should be a integer. Check your Vars!"))
            elif not attr in object_attrs[object_type]:
                module.fail_json(msg=("Attribute " + attr + " is not a valid part of the object type " + object_type))


    def run(self):
        config = ''

        if re.search(r'(object|template|apply)', self.state) and not (self.apply_target and self.apply):
            config += '%s %s %s {\n' % (self.state, self.object_type, i2_lookup.parser(row=self.object_name))
        elif self.state == 'apply' and self.object_type == 'Service':
            config += 'apply Service "%s " for (%s)' % (i2_lookup.parse(self.object_name), self.apply)
        elif self.state == 'apply' and re.match(r'^(Notification|Dependency)$', self.object_type):
            config += 'apply %s "%s" to %s' % (self.object_type, self.object_name, self.apply_target)
        for imp in self.imports:
            config += '  import "%s"\n' % (imp)
            config += '\n'
        if self.attrs:
            config += '  %s' % (re.sub('\n','\n  ', i2_lookup.icinga2_parser(self.attrs)))
            config += '\n'
        if self.vars and bool(self.vars):
            config += '  %s' % (re.sub('\n','\n  ', i2_lookup.icinga2_parser(self.vars)))
            config += '\n'
        if self.assign:
            print(self.assign)
            config += '  %s' % (re.sub('\n','\n  ', i2_lookup.icinga2_parser(self.assign)))
            config += '\n'
        config += "}"

        obj = dict(changed=True, ansible_module_results="object generated", object=config)
        return obj




def main():
    global module
    object_types = [
        'Host',
        'Service',
        'ApiUser',
        'CheckCommand',
        'Dependency',
        'Endpoint',
        'EventCommand',
        'HostGroup',
        'Notification',
        'NotificationCommand',
        'ScheduledDowntime',
        'ServiceGroup',
        'TimePeriod',
        'User',
        'UserGroup',
        'Zone',
        'ApiListener',
        'CheckerComponent',
        'CheckResultReader',
        'CompatLogger',
        'ElasticsearchWriter',
        'ExternalCommandListener',
        'FileLogger',
        'GelfWriter',
        'GraphiteWriter',
        'IcingaApplication',
        'IcingaDB',
        'IdoMysqlConnection',
        'IdoPgsqlConnection',
        'InfluxdbWriter',
        'LivestatusListener',
        'NotificationComponent',
        'OpenTsdbWriter',
        'PerfdataWriter',
        'StatusDataWriter',
        'SyslogLogger'
    ]

    module = AnsibleModule(
        argument_spec=dict(
            object_name=dict(required=True),
            object_type=dict(required=True, choices=object_types),
            state=dict(required=True, choices=['template','object','apply','absent']),
            attrs=dict(type=dict),
            vars=dict(type=dict),
            imports=dict(type=list),
            assign=dict(type=dict),
            apply=dict(type=str),
            apply_target=dict(type=str, choices=['Host','Service']),
            constants=dict(type=dict)



        ),
        supports_check_mode=False,
    )

    result = Icinga2Objects().run()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
