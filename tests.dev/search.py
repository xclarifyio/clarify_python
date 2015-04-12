#!/usr/bin/env python

"""
Some test functions used to sanity check during development. Not
unit tests.
"""

import sys
sys.path.insert(0, '..')
from clarify_python import clarify

def simple_search(client):
    """This function performs no setup, so we don't even check the
    results.  Just a basic sanity check."""

    print('*** Searching for "father"...')
    print(client.search(None, 'father'))


def all_tests(apikey):
    """Set API key and call all test functions."""

    client = clarify.Client(apikey)

    print('===== simple_search() =====')
    simple_search(client)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print('Usage: ' + sys.argv[0] + ' <apikey>')
        exit(1)

    all_tests(sys.argv[1])
