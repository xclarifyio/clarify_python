#!/usr/bin/env python

"""
Some test functions used to sanity check during development. Not
unit tests.
"""

import sys
sys.path.insert(0, '..')
from clarify_python import clarify

def delete_bundle(client, href):
    """Delete bundle at href."""

    print('*** Deleting ' + href)
    client.delete_bundle(href)


def delete_all_bundles(client):
    """Delete all bundles."""

    client.bundle_list_map(delete_bundle)


def all_tests(apikey):
    """Set API key and call all test functions."""

    client = clarify.Client(apikey)

    print('===== delete_all_bundles() =====')
    delete_all_bundles(client)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print('Usage: ' + sys.argv[0] + ' <apikey>')
        exit(1)

    all_tests(sys.argv[1])
