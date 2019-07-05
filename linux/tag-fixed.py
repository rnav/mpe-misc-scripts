#!/usr/bin/python3
#
# Tag commits as being fixed by one or more subsequent Fixes: commits.
#
# Usage:
#  $ git rev-list v4.0.. [ optional path ] | tag-fixed.py
#

import os
import re
import sys
from subprocess import call, check_call, check_output, getstatusoutput


def verify_sha(sha):
    cmd = 'git rev-parse -q --verify %s^{commit}' % sha
    rc, output = getstatusoutput(cmd)
    if rc != 0:
        return None
    return output.strip()


def main():
    FIXES_PATT = re.compile('Fixes: ([a-fA-F0-9]+) .*')

    total = 0
    fixes = 0
    already_marked = 0
    not_found = 0
    marked = 0
    for sha in sys.stdin.readlines():
        sha = sha.strip()
        total += 1

        cmd = 'git cat-file -p %s' % sha
        log = check_output(cmd.split()).decode('utf-8')

        match = FIXES_PATT.search(log)
        if not match:
            continue

        fixes += 1
        fixed = match.group(1)

        verified = verify_sha(fixed)
        if verified is None:
            print("Couldn't find commit", fixed, "fixed by", sha)
            not_found += 1
            continue

        fixed = verified

        # If things get messed up uncomment this to remove existing notes
        #cmd = ['git', 'notes', '--ref=fixed', 'remove', fixed]
        #call(cmd)

        cmd = ['git', 'log', '-1', '--format=Fixed-by: %h ("%s")', sha]
        fixed_by = check_output(cmd).decode('utf-8').strip()

        cmd = 'git notes --ref=fixed show %s' % fixed
        rc, note_body = getstatusoutput(cmd)
        if rc == 0 and fixed_by in note_body:
            #print("Already marked commit %s as fixed by %s" % (fixed, sha))
            already_marked += 1
            continue

        cmd = ['git', 'notes', '--ref=fixed', 'append', '-m', fixed_by, fixed]
        check_call(cmd)

        #print("Marked commit %s as fixed by %s" % (fixed, sha))
        marked += 1

    print("Scanned %d commits, found %d fixes." % (total, fixes))
    print("Marked %d commits as fixed, %d already marked, %d not found." % (marked, already_marked, not_found))


main()
