#!/usr/bin/env python
# coding: utf-8

# For python 2 compatibility
from __future__ import unicode_literals
import sys
from os.path import split, join, exists
from os import getcwd, mkdir
import subprocess


# Python Version Compatibility
major = sys.version_info[0]
minor = sys.version_info[1]

if major < 3:
    rinput = raw_input
else:
    rinput = input

if major == 2 and minor == 6:
    check_output = lambda a: subprocess.Popen(a,
            stdout=subprocess.PIPE).communicate()[0]
else:
    check_output = subprocess.check_output


COLOR = ['git', 'config', '--get', 'gitli.color']
GITLIDIR = '.gitli'

ISSUES = '.issues'
OPEN = '.issues-open'
LAST = '.issues-last'
CURRENT = '.issues-current'
COMMENTS = '.issues-comments'
MSEPARATOR = ','
OSEPARATOR = '\n'

TTYPES = ['Task', 'Bug', 'Enhancement']


class BColors:
    BLUE = '\033[1;34m'
    GREEN = '\033[1;32m'
    YELLOW = '\033[1;33m'
    CYAN = '\033[1;36m'
    WHITE = '\033[1;37m'
    ENDC = '\033[0m'

    def disable(self):
        self.BLUE = ''
        self.GREEN = ''
        self.YELLOW = ''
        self.CYAN = ''
        self.WHITE = ''
        self.ENDC = ''


def is_colored_output():
    try:
        value = check_output(COLOR).strip().lower().decode('utf-8')
        return value in ('auto', 'on', 'true')
    except Exception:
        return False


def ask_type(verbose=False, default=1):
    if not verbose:
        return 1

    ttype = rinput('Task type: 1-Task, 2-Bug, 3-Enhancement [{0}]: '\
            .format(default))
    ttype = ttype.strip().lower()

    if not ttype:
        return default
    elif ttype in ('1', 'task'):
        return 1
    elif ttype in ('2', 'bug'):
        return 2
    elif ttype in ('3', 'enhancement'):
        return 3
    else:
        return 1


def ask_milestone(path, verbose=False, default=None):
    if default is None:
        current = open(join(path, CURRENT), 'r')
        current_value = current.read()
        current.close()
    else:
        current_value = default

    if not verbose:
        return current_value

    milestone = rinput('Milestone: [{0}]: '.format(current_value)).strip()
    if not milestone:
        milestone = current_value

    return milestone


def add_open(path, issue_number):
    iopen = open(join(path, OPEN), 'a')
    iopen.write('{0}{1}'.format(issue_number, OSEPARATOR))
    iopen.close()


def remove_open(path, issue_number):
    iopen = open(join(path, OPEN), 'r')
    issues = iopen.read().split(OSEPARATOR)
    iopen.close()

    new_issues = OSEPARATOR.join((issue for issue in issues if issue !=
        issue_number))

    iopen = open(join(path, OPEN), 'w')
    iopen.write(new_issues)
    iopen.close()


def get_open_issues(path):

    iopen = open(join(path, OPEN), 'r')
    issues = iopen.read().split(OSEPARATOR)
    iopen.close()

    return issues


def filter_issues(issue, filters, open_issues, milestones, tasks):
    if 'open' in filters and issue[0] not in open_issues:
        return False

    if 'close' in filters and issue[0] in open_issues:
        return False

    if len(milestones) > 0 and issue[3] not in milestones:
        return False

    if len(tasks) > 0 and TTYPES[issue[2] - 1].lower() not in tasks:
        return False

    return True


def get_issue(path, issue_number):
    issues_file = open(join(path, ISSUES), 'r')
    lines = issues_file.readlines()
    issues_file.close()
    size = len(lines)
    index = 0
    issue = None
    while index < size:
        issue = (
            lines[index].strip(),
            lines[index + 1].strip(),
            int(lines[index + 2].strip()),
            lines[index + 3].strip())
        if issue[0] == issue_number:
            break
        else:
            issue = None
            index += 4

    return issue


def get_issues(path, filters, open_issues, milestones, tasks):
    issues_file = open(join(path, ISSUES), 'r')
    lines = issues_file.readlines()
    issues_file.close()
    issues = []
    size = len(lines)
    index = 0
    while index < size:
        issue = (
            lines[index].strip(),
            lines[index + 1].strip(),
            int(lines[index + 2].strip()),
            lines[index + 3].strip())
        if filter_issues(issue, filters, open_issues, milestones, tasks):
            issues.append(issue)
        index += 4

    return issues


def print_issues(issues, open_issues, bcolor):
    for (number, title, task_id, milestone) in issues:
        if number in open_issues:
            open_text = 'open'
            color = bcolor.YELLOW
        else:
            open_text = 'closed'
            color = bcolor.GREEN

        milestone_text = '[' + milestone + ']'
        task_text = '[' + TTYPES[task_id - 1] + ']'

        print('{5}#{0:<4}{9} {6}{1:<48}{9} {7}{2:<6} {3:<7}{9} - {8}{4}{9}'
            .format(number, title, task_text, milestone_text, open_text,
            bcolor.CYAN, bcolor.WHITE, bcolor.BLUE, color, bcolor.ENDC))


def init(path):
    if not exists(path):
        mkdir(path)

    new_path = join(path, ISSUES)
    if not exists(new_path):
        open(new_path, 'w').close()

    new_path = join(path, OPEN)
    if not exists(new_path):
        open(new_path, 'w').close()

    new_path = join(path, COMMENTS)
    if not exists(new_path):
        open(new_path, 'w').close()

    new_path = join(path, LAST)
    if not exists(new_path):
        last = open(new_path, 'w')
        last.write('0')
        last.close()

    new_path = join(path, CURRENT)
    if not exists(new_path):
        current = open(new_path, 'w')
        current.write('0.1')
        current.close()


def new_issue(path, title, verbose=False):
    last = open(join(path, LAST), 'r')
    issue_number = int(last.read().strip()) + 1
    last.close()

    ttype = ask_type(verbose)
    milestone = ask_milestone(path, verbose)

    issues = open(join(path, ISSUES), 'a')
    issues.write('{0}\n{1}\n{2}\n{3}\n'.format(issue_number, title,
        ttype, milestone))
    issues.close()

    add_open(path, issue_number)

    last = open(join(path, LAST), 'w')
    last.write('{0}'.format(issue_number))
    last.close()


def close_issue(path, issue_number):
    remove_open(path, issue_number)


def list_issues(path, filters=None, bcolor=BColors()):
    if filters is None:
        filters = []
    else:
        filters = [ifilter.strip().lower() for ifilter in filters]

    open_issues = get_open_issues(path)

    tasks = [ifilter for ifilter in filters if ifilter in
        ('task', 'bug', 'enhancement')]

    milestones = [ifilter for ifilter in filters if ifilter not in
        ('open', 'close', 'task', 'bug', 'enhancement')]

    issues = get_issues(path, filters, open_issues, milestones, tasks)

    print_issues(issues, open_issues, bcolor)


def reopen_issue(path, issue_number):
    # To make sure that we don't add the issue twice... that would be bad
    remove_open(path, issue_number)
    add_open(path, issue_number)


def show_issue(path, issue_number, bcolor=BColors()):
    issue = get_issue(path, issue_number)
    if issue is not None:
        open_issues = get_open_issues(path)
        print_issues([issue], open_issues, bcolor)
    else:
        print('Issue #{0} not found'.format(issue_number))


def edit_issue(path, issue_number):
    issues = get_issues(path, [], [], [], [])
    issue = None
    index = -1
    for i, temp_issue in enumerate(issues):
        if temp_issue[0] == issue_number:
            issue = temp_issue
            index = i

    if issue is None:
        print('Issue #{0} unknown'.format(issue_number))
        return
    else:
        title = rinput('Enter a new title (enter nothing to keep the same): ')
        if not title.strip():
            title = issue[1]
        ttype = ask_type(True, issue[2])
        milestone = ask_milestone(path, True, issue[3])
        new_issue = (issue_number, title, ttype, milestone)

        issues_file = open(join(path, ISSUES), 'w')
        for i, temp_issue in enumerate(issues):
            if i != index:
                issues_file.write('{0}\n{1}\n{2}\n{3}\n'.format(temp_issue[0],
                    temp_issue[1], temp_issue[2], temp_issue[3]))
            else:
                issues_file.write('{0}\n{1}\n{2}\n{3}\n'.format(new_issue[0],
                    new_issue[1], new_issue[2], new_issue[3]))

        issues_file.close()


def edit_milestone(path, milestone):
    if milestone:
        current_path = join(path, CURRENT)
        current = open(current_path, 'w')
        current.write(milestone)
        current.close()


def show_milestone(path):
    current_path = join(path, CURRENT)
    current = open(current_path, 'r')
    milestone = current.read().strip()
    current.close()
    print('The current milestone is {0}'.format(milestone))


def main(options, args, parser):
    bcolor = BColors()
    if not is_colored_output():
        bcolor.disable()

    if len(args) == 0:
        parser.print_help()
        sys.exit(1)

    command = args[0]
    args = args[1:]
    path = getcwd()
    while not exists(join(path, ".git")):
        path, extra = split(path)
        if not extra:
            print("Unable to find a git repository. ")
            sys.exit(1)

    path = join(path, GITLIDIR)
    if command == 'init':
        init(path)
    elif command in ('new', 'add'):
        new_issue(path, args[0].strip(), options.edit)
    elif command == 'close':
        close_issue(path, args[0].strip())
    elif command == 'list':
        list_issues(path, args, bcolor)
    elif command == 'reopen':
        reopen_issue(path, args[0].strip())
    elif command == 'show':
        show_issue(path, args[0].strip(), bcolor)
    elif command == 'edit':
        edit_issue(path, args[0].strip())
    elif command == 'milestone':
        if len(args) == 0:
            show_milestone(path)
        else:
            edit_milestone(path, args[0].strip())
