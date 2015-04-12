#!/usr/bin/env python

"""
Some test functions used to sanity check during development. Not
unit tests.
"""

import sys
sys.path.insert(0, '..')
from clarify_python import clarify

def metadata_delete(client):
    """Create a bundle with metadata, print it, delete it, print it."""

    # Create a bundle with some metadata.
    print('*** Creating a bundle with mythical metadata...')
    data = {'wife': 'Medea', 'husband': 'Jason'}
    bundle_ref = client.create_bundle(name='metadata update test',
                                      metadata=data)

    # Retrieve the metadata and print it.
    print('*** Retrieving metadata...')
    metadata_href = bundle_ref['_links']['clarify:metadata']['href']
    metadata = client.get_metadata(metadata_href)
    print_metadata_info_quiet(metadata)

    # Delete the metadata and print it.
    print('*** Deleting metadata...')
    client.delete_metadata(metadata['_links']['self']['href'])

    # Retrieve the metadata and print it.
    print('*** Retrieving metadata...')
    metadata = client.get_metadata(metadata_href)
    print_metadata_info_quiet(metadata)


def print_metadata_info(metadata):
    """Print metadata."""

    print('** Metadata info')
    print('* Created: ' + metadata['created'])
    print('* Updated: ' + metadata['updated'])
    if 'data' in metadata:
        print('* Data: ' + str(metadata['data']))


def print_metadata_info_quiet(metadata):
    """Print condensed version of metadata."""

    if 'data' in metadata:
        print(str(metadata['data']))


def all_tests(apikey):
    """Set API key and call all test functions."""

    client = clarify.Client(apikey)

    print('===== metadata_delete() =====')
    metadata_delete(client)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print('Usage: ' + sys.argv[0] + ' <apikey>')
        exit(1)

    all_tests(sys.argv[1])
