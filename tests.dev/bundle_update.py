#!/usr/bin/env python

"""
Some test functions used to sanity check during development. Not
unit tests.
"""

import sys
sys.path.insert(0, '..')
from clarify_python import clarify


def update_all_bundle_names(client):
    """Update and print all the bundle names.
    Will fail if no bundles are available!"""

    client.bundle_list_map(update_name)
    client.bundle_list_map(print_name)


def update_name(client, href):
    """Update the name of the bundle at href."""

    bundle = client.get_bundle(href)
    name = bundle.get('name')
    if name is None:
        name = 'no name updated'
    else:
        name = name + ' updated'
        print('*** Updating name for ' + href)
    client.update_bundle(href, name)


def print_name(client, href):
    """Print the name of the bundle at href."""

    bundle = client.get_bundle(href)
    print('*** ' + href + ' is now named "' + bundle['name'] + '"')


def all_tests(apikey):
    """Set API key and call all test functions."""

    client = clarify.Client(apikey)

    print('===== update_all_bundle_names() =====')
    update_all_bundle_names(client)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print('Usage: ' + sys.argv[0] + ' <apikey>')
        exit(1)

    all_tests(sys.argv[1])
