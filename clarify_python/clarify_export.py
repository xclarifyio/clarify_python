#!/usr/bin/env python3
import sys
import os
import json
from clarify_python import clarify
from clarify_python.helper import get_embedded, get_link_href


CLARIFY_API_KEY = os.environ.get('CLARIFY_API_KEY')
OUTPUT_PATH = ''


def write_json(basename, typename, content):
    filename = basename + '-' + typename + '.json'
    with open(os.path.join(OUTPUT_PATH, filename), 'w') as out:
        out.write(json.dumps(content, indent=2))


def fetch_insight(client, basename, insights, insight_rel):
    link = get_link_href(insights, insight_rel)
    if link:
        data = client.get_insight(link)
        write_json(basename, insight_rel[8:], data)


def process_bundle(client, href):
    print("Bundle " + href)
    bundle = client.get_bundle(href, embed_tracks=True, embed_metadata=True, embed_insights=True)
    name = bundle.get('external_id')
    if not name:
        name = bundle.get('name')
        if not name:
            name = bundle['id']

    basename, file_extension = os.path.splitext(name)

    data = get_embedded(bundle, 'clarify:tracks')
    write_json(basename, 'tracks', data)

    data = get_embedded(bundle, 'clarify:metadata')
    write_json(basename, 'metadata', data)

    insights = get_embedded(bundle, 'clarify:insights')
    # print(insights)
    insight_links = insights['_links']

    for link_rel in insight_links.keys():
        # we don't use insight:transcript because it's an alias
        if link_rel.startswith('insight:') and link_rel != 'insight:transcript':
            fetch_insight(client, basename, insights, link_rel)


def main():
    if len(sys.argv) != 2 or CLARIFY_API_KEY is None or len(CLARIFY_API_KEY) == 0:
        print("\nUsage: " + sys.argv[0] + ' <output_folder>')
        print("\nExport all data for a Clarify account (based on the CLARIFY_API_KEY env var) ")
        print("Writes the files to <output_folder>.")
        print("")
        sys.exit(-1)

    global OUTPUT_PATH
    OUTPUT_PATH = sys.argv[1]
    if not os.path.isdir(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    try:
        client = clarify.Client(CLARIFY_API_KEY)
        client.bundle_list_map(process_bundle)
    except clarify.APIException as e:
        print("{0}: {1}".format(e.get_status(), e.get_http_response()))
        raise

if __name__ == "__main__":
    main()
