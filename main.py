# -*- coding: utf-8 -*-
"""
Simple windows notepad.exe todo notes parser 
 - makes use of F5 timestamp in notepad.exe: 23:30 06.02.2016
 - aims to convert .txt file to a datastructure of tasks with subtasks/timestamps. 
 - similar in spririt to http://todotxt.com/
"""

from datetime import datetime
import re


def ts_to_datetime(timestamp):
    return datetime.strptime(timestamp.strip(), '%H:%M %d.%m.%Y')

assert ts_to_datetime('23:30 06.02.2016') == datetime(2016, 2, 6, 23, 30)
assert ts_to_datetime('1:10 06.02.2016') == datetime(2016, 2, 6, 1, 10)
assert ts_to_datetime(' 23:30 06.02.2016  ') == datetime(2016, 2, 6, 23, 30)

# catches one letter inside brackets, like '[d]'
STATUS_PAT = re.compile(r'\s*\[\s*(\w)\s*\]\s*')

# catches notepad.exe F5 timestamp
DATETIME_PAT = re.compile(r'\s*([012]?\d:\d\d [0123]\d\.[01]\d\.\d\d\d\d)\s*')


def get_status_letter(string, status_re = STATUS_PAT):
    status_list = status_re.findall(string)
    if len(status_list) > 0:
        return status_list[0]

# note will skip [x] after first occurence
assert get_status_letter('[s] [z]') == 's'
assert get_status_letter('[s][z]') == 's'
assert get_status_letter('dd [] sdff [s]  [z]') == 's'
assert not get_status_letter('dd [1] sdff [s]  [z]') == 's'
assert get_status_letter('[abc]') is None


def get_datetime_list(string, datetime_re = DATETIME_PAT):
    return map(ts_to_datetime, datetime_re.findall(string))


assert get_datetime_list('    some [a] 23:30 06.02.2016 description') == [datetime(2016, 2, 6, 23, 30)]

datetime_list_sample = [
    datetime(2016, 2, 6, 23, 30),
    datetime(2016, 2, 6, 23, 31)
]
assert get_datetime_list('    some [a] 23:30 06.02.2016 23:31 06.02.2016 description') == datetime_list_sample
assert get_datetime_list('    some [a] 23:30 06.02.2016 fd 23:31 06.02.2016 description') == datetime_list_sample


def get_description(s, status_re = STATUS_PAT, datetime_re = DATETIME_PAT):
    s = datetime_re.sub(' ', s)
    s = status_re.sub(' ', s)
    return s.strip()

assert get_description('    some [a] 23:30 06.02.2016 description') == 'some description'
assert get_description('    some [a] 23:30 06.02.2016 23:30 06.02.2016 description') == 'some description'
assert get_description('    [a] some 23:30 06.02.2016 description') == 'some description'
assert get_description('    [a] 23:30 06.02.2016 some description') == 'some description'
assert get_description('    [a] 23:30 06.02.2016 some description ') == 'some description'
assert get_description('    [a]  23:30 06.02.2016 some description ') == 'some description'
assert get_description('    [a] 23:30 06.02.2016  some description ') == 'some description'

assert get_description('    some [a] 23:30 06.02.2016 ... 23:30 06.02.2016 description') == 'some ... description'


def parse_subtask(s):
    result = {
        'status': None,
        'last checked': None,
        'started': None,
        'ended': None,
        'desc': '' # EP: not sure it is not None
    }

    # get status letter like 's' from '[s]' 
    result['status'] = get_status_letter(s)

    # get timestamps, allocate to dictionary 
    datetime_list = get_datetime_list(s)
    if len(datetime_list) == 1:
        result['last checked'] = datetime_list[0]
    elif len(datetime_list) == 2:
        result['started'] = datetime_list[0]
        result['ended'] = datetime_list[1]

    # get testxline description for subtask
    result['desc'] = get_description(s)

    return result


#rules for parsing doc2:
#    text starting with no offset (at start of string) is title
#    four spaces offset is subtask line 

# parsing subtasks 
#    single letter in square brackets anywhere in subtask line is status flag + only one [x] is taken 
#    one timestamp is 'last checked' date and time 
#    two timestamps is 'started' and 'ended' date and time 
#    remaining text after popping out status and timestamp(s) is 'desc'

doc2 = """worktitle
    subtask description 23:30 06.02.2016
    23:30 06.02.2016 23:36 06.02.2016 subtask description 2
    [s] 23:30 06.02.2016 subtask description 3"""


subtask_dict_sample = {
    'status': 's',
    'last checked': None,
    'started':      datetime(2016, 2, 6, 23, 30),
    'ended':        datetime(2016, 2, 9, 2, 30),
    'desc':         'subtask description 3'
}

assert not subtask_dict_sample == parse_subtask('[s] 23:30 06.02.2016 ... 2:30 09.02.2016 subtask description 3') # TO CLEAR UP
assert subtask_dict_sample == parse_subtask('[s] 23:30 06.02.2016 2:30 09.02.2016 subtask description 3')
assert subtask_dict_sample == parse_subtask('[s] subtask description 3 23:30 06.02.2016 2:30 09.02.2016')
# more whitespace
assert subtask_dict_sample == parse_subtask('[s]    subtask description 3     23:30 06.02.2016    2:30 09.02.2016   ')



##############
# May delete #
##############

#ref_yaml_parsed = {'worktitle': [   
#  [ '', '23:30 06.02.2016', '', 'subtask description 1']
#, [ '', '23:30 06.02.2016', '23:36 06.02.2016', 'subtask description 2']
#, ['s', '23:30 06.02.2016', '', 'subtask description 3']
#]}


# for reference
# print (yaml.dump(ref_yaml_parsed))

# def parse_yml(string):
#     parsed = yaml.parse(doc1)
#     for k, v in parsed.iteritems():
#         if type(v) == list:
#             parsed[k] = subtask_to_list(v)
#     return parsed

# assert parse_yml(doc1) == ref_yaml_parsed


#doc1 = """worktitle:
#- subtask description 23:30 06.02.2016
#- 23:30 06.02.2016 23:36 06.02.2016 subtask description 2
#- [s] 23:30 06.02.2016 subtask description 3"""
