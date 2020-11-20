# python 3 headers, required if submitting to Ansible
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = """
        lookup: icinga2_attributes
        author: Thilo Wening
        version_added: "0.1"
        short_description: generate icinga2 attributes
        description:
            - blubber
        notes:
          - if read in variable context, the file can be interpreted as YAML if the content is valid to the parser.
          - this lookup does not understand globing --- use the fileglob lookup instead.
"""
from ansible.plugins.lookup import LookupBase
import re

class i2_lookup(LookupBase):


    def attribute_types(self, attr):
        if re.search(r'^[a-zA-Z0-9_]+$', attr):
            result = attr
        else:
            result = '"'+ attr + '"'
        return result
        
    def value_types(self, value, indent=2):

        # Values without quotes
        if ((r := re.search(r'^-?\d+\.?\d*[dhms]?$', value)) or (r := re.search(r'^(true|false|null)$', value)) or
            ( r := re.search(r'^!?(host|service|user)\.', value))):
            result = value
        elif value in self.constants:
            # Check if it is a constant
            result = value
        else:
            # Print a normal string
            result = '"' + value + '"'
        return result

    def parser(self, row):
        result = ''
        #print(row)

        # Disable parsing of the value
        if (r := re.search(r'^-:(.*)$', row)):
            #print("Ignore Row: " + row)
            return r.group(1)

        # r = re.search(r'^\{{2}(.+)\}{2}$', row)
        if (r := re.search(r'^\{{2}(.+)\}{2}$', row)):
            #Ex. '{{ testfuction in icinga2 }}'
            #print("Im a Function: " + row)
            result += "{{ %s }}" % (r.group(1))
        elif (r := re.search(r'^(.+)\s([\+-]|\*|\/|==|!=|&&|\|{2}|in)\s\{{2}(.+)\}{2}$', row)):
            #print("Im a expression with a function " + row )
            result += "%s %s {{ %s }}" % (i2_lookup.parser(r.group(1)), r.group(2), r.group(3))
        elif (r := re.search(r'^(.+)\s([\+-]|\*|\/|==|!=|&&|\|{2}|in)\s(.+)$', row)):
            #print("Im a expression maybe assign " + row)
            result += "%s %s %s" % (i2_lookup.parser(r.group(1)), r.group(2), i2_lookup.parser(r.group(3)))
        else:
            if (r := re.search(r'^(.+)\((.*)$', row)):
                #print("Irgendwas mit klammer %s(%s wahrscheinlich match(): " + row)
                result += "Parser kommt noch"
                # Alle Params der Funktion werden einzeln ohne Komma dem Parser übergeben und danach wieder zusammengeführt.
                # result += "%s(%s" % [ $1, $2.split(',').map {|x| parse(x.lstrip)}.join(', ') ]
            elif (r := re.search(r'^ (.*)\)(.+)?$', row)):
                print("# closing bracket ) with optional access of an attribute e.g. '.arguments'" +
                      'result += "%s)%s" % [ $1.split(', ').map {|x| parse(x.lstrip)}.join(', '), $2 ]"')
            elif (r := re.search(r'^\((.*)$', row)):
                result += "(%s" % (i2_lookup.parser(r.group(1)))
            elif (r := re.search(r'^\s*\[\s*(.*)\s*\]\s?(.+)?$', row)):
                #print("Its an array - process it " + row)
                result += "[ %s]" % (i2_lookup.process_array(r.group(1).split(',')))
                if r.group(2):
                    result += " %s" % (i2_lookup.parser(r.group(2)))
            elif (r := re.search(r'^\s*\{\s*(.*)\s*\}\s?(.+)?$', row)):
                #print("Its an hash " + row)
                result += "%s" % (i2_lookup.process_hash(dict(list(i2_lookup.divide_chunks((re.sub('\s*=\s*|\s*,\s*', ',', r.group(1)).split(',')), 2)))))
                if r.group(2):
                    result += " %s" % (i2_lookup.parser(r.group(2)))
            else:
                result += str(i2_lookup.value_types(row.lstrip(' ')))

        return result

    def process_array(self, items, indent=2):
        result=''

        #print("ident=" + str(indent))

        for item in items:
            #print("Item="+item)
            if type(item) is dict:
                result += "\n%s{\n%s%s}, " % ( ' '*indent, i2_lookup.process_hash(attrs=value, indent=indent+2), ' '*indent)
            elif type(item) is list:
                result += "[ %s], " % ( i2_lookup.process_array(item.split(','), indent=indent+2))
            else:
                result += "%s, " % (i2_lookup.parser(item))
        return result

    def process_hash(self, attrs, level=3, indent=2, prefix=' '):
        result = ''
        if re.search(r'^\s+$', prefix):
            prefix = prefix * indent
        op = ''

        #print("Hello to parser " + str(attrs))

        for attr, value in attrs.items():
            #print(attr)
            if type(value) is dict:
                #print("Im a dict: " + str(value))
                if "+" in value:
                    #print("delete value with +")
                    del value['+']
                    op = "+"
                    #print(value)
                if not bool(value):
                    #print("Its empty- moving on")
                    if level == 1:
                        #print("empty level1")
                        result += "%s%s %s={}\n" % (prefix, attr, op)
                    elif level == 2:
                        #print("empty level2")
                        result += "%s[\"%s\"] %s= {\n%s%s}\n" % (
                        prefix, attr, op, i2_lookup.process_hash(attrs=value, indent=indent+2), ' '*indent)
                    else:
                        #print("empty level3")
                        result += "%s%s %s= {\n%s%s}\n" % (
                        prefix, i2_lookup.attribute_types(attr), op, i2_lookup.process_hash(attrs=value, indent=indent+2), ' '*indent)

                # "%s%s #{op}= {\n%s%s}\n" % [prefix, attribute_typess(attr), process_hash(value, indent + 2), ' ' * indent]
                else:
                    #print("Next Level for: " + str(value))
                    #print(indent)
                    indent_char=' '
                    if level == 1:
                        result += i2_lookup.process_hash(attrs=value, level=2, indent=indent, prefix=(prefix + attr))
                    elif level == 2:
                        result += "%s[\"%s\"] %s= {\n%s%s}\n" % (
                        prefix, attr, op, i2_lookup.process_hash(attrs=value, indent=indent), (indent-2)*indent_char)
                    else:
                        result += "%s%s %s= {\n%s%s}\n" % (
                        prefix, i2_lookup.attribute_types(attr), op, i2_lookup.process_hash(attrs=value, indent=indent+2), ' '*indent)
            elif type(value) is list:
                if value[0] == "+":
                    op = "+"
                    value.pop(0)
                elif value[0] == "-":
                    op = "-"
                    value.pop(0)
                if level == 2:
                    result += "%s[\"%s\"] %s= [ %s]\n" % (
                    prefix, i2_lookup.attribute_types(attr), op, i2_lookup.process_array(value))
                else:
                    result += "%s%s %s= [ %s]\n" % (
                    prefix, i2_lookup.attribute_types(attr), op, i2_lookup.process_array(value))
            else:
                if (r := re.search(r'^([\+,-])\s+', value)):
                    operator = r.group(1)
                    value = re.sub(r'^[\+,-]\s+/', '', value)
                else:
                    operator = ''
                if level > 1:
                    if level == 3:
                        if value != None:
                            result += "%s%s %s= %s\n" % (
                            prefix, i2_lookup.attribute_types(attr), operator, i2_lookup.parser(value))
                    else:
                        if value != None:
                            result += "%s[\"%s\"] %s= %s\n" % (prefix, attr, operator, i2_lookup.parser(value))
                else:
                    if value != None:
                        result += "%s%s %s= %s\n" % (prefix, attr, operator, i2_lookup.parser(value))

        return result

    def divide_chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]



    def icinga2_parser(self, attrs):
        config = ''
        indent = 0
        op = ''

        for attr, value in attrs.items():

            if re.search(r'^(assign|ignore) where$', attr):
                for x in value:
                  config += "%s%s %s\n" % (' '*indent, attr, i2_lookup.parser(x))
            elif attr == 'vars':
                if type(value) is dict:
                    if "+" in value:
                        del value['+']
                    config += i2_lookup.process_hash(attrs=value, indent=indent+2, level=1, prefix=("%s%s." % (' '*indent, attr)))
                elif type(value) is list:
                    for item in value:
                        if type(item) is str:
                            config += "%s%s += %s\n" % (indent*' ', attr, re.sub(r'^[\+,-]\s+/', '', item))
                        else:
                            if "+" in item:
                                del item["+"]
                            if not bool(item):
                                config += "%s%s += {}\n" % ( ' ' * indent, attr)
                            else:
                                config += i2_lookup.process_hash(attrs=item, indent=indent+2, level=1, prefix=("%s%s." % (' '*indent, attr)))
                else:
                    op = '+' if re.search(r'^\+\s+', value) else None
            else:
                if type(value) is dict:
                    if "+" in value:
                        op = '+'
                        del value['+']
                    if bool(value):
                        config += "%s%s %s= {\n%s%s}\n" % (' '*indent, attr, op, i2_lookup.process_hash(attrs=value, indent=indent+2), ' '*indent)
                    else:
                        config += "%s%s %s= {}\n" % (' '*indent, op, attr)
                elif type(value) is list:
                    if value[0] == "+":
                        op = "+"
                        value.pop(0)
                    elif value[0] == "-":
                        op = "-"
                        value.pop(0)
                    config += "%s%s %s= [ %s]\n" % ( ' ' * indent, attr, op, i2_lookup.process_array(value))
                else:
                    if ( r:=re.search(r'^([\+,-])\s+', str(value))):
                        config += "%s%s %s= %s\n" % (' '*indent, attr, op, i2_lookup.parser(re.sub(r'^[\+,-]\s+', '', str(value))))
                    else:
                        config += "%s%s = %s\n" % (' '*indent, attr, i2_lookup.parser(str(value)))
        return config

    def __init__(self):
        self.constants=['NodeName']








# def run(self, vars, **kwargs):
#         print(self)
#
# def value_types(value):
#       if value is match('^\d+(ms|s|h|d)?$') or value is match('^(true|false|null)$') or value is match('^!?(host|service|user)\.') or value is match('^\{{2}.*\}{2}$'):
#         result = value
#
#       return result
#
#
# def parser(row):
#   result = ''
#   # parser is disabled
#   r = re.compile(r'^-:(.*)$')
#   if bool(r.search(row)):
#     return r.search(row).group(1)
