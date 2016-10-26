import sys
import os
import re

if sys.version_info[0] < 3:
    from io import open


host = 'https://api.clarify.io'


def load_body(filename):
    text = None
    with open(os.path.join('.', 'tests', 'data', filename), encoding="utf-8") as f:
        text = f.read()
    return text if text else '{}'


def register_uris(httpretty):

    httpretty.register_uri('POST', host + '/v1/bundles',
                           body=load_body('bundle_ref.json'), status=201,
                           content_type='application/json')

    httpretty.register_uri('GET', host + '/v1/bundles',
                           body=load_body('bundles_1.json'), status=200,
                           content_type='application/json')

    httpretty.register_uri('GET', re.compile(host + '/v1/bundles/(\w+)\?embed=(.*)$'),
                           body=load_body('bundle_embedded.json'), status=200,
                           content_type='application/json', match_querystring=True)

    httpretty.register_uri('GET', re.compile(host + '/v1/bundles/(\w+)$'),
                           body=load_body('bundle.json'), status=200,
                           content_type='application/json', match_querystring=True)

    httpretty.register_uri('GET', re.compile(host + '/v1/bundles/(\w+)/tracks$'),
                           body=load_body('tracks.json'), status=200,
                           content_type='application/json')

    httpretty.register_uri('GET', re.compile(host + '/v1/bundles/(\w+)/metadata$'),
                           body=load_body('metadata.json'), status=200,
                           content_type='application/json')

    httpretty.register_uri('GET', re.compile(host + '/v1/bundles/(\w+)/insights$'),
                           body=load_body('insights.json'), status=200,
                           content_type='application/json')

    httpretty.register_uri('GET', re.compile(host + '/v1/bundles/(\w+)/insights/(\w+)$'),
                           body=load_body('insight_classification.json'), status=200,
                           content_type='application/json')

    httpretty.register_uri('POST', re.compile(host + '/v1/bundles/(\w+)/insights$'),
                           body=load_body('insight_pending.json'), status=202,
                           content_type='application/json')
