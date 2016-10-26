import unittest
import httpretty
try:
    from urllib.parse import parse_qs
except ImportError:
     from urlparse import parse_qs
from clarify_python.clarify import Client
from clarify_python.helper import get_embedded, get_link_href
from . import register_uris


class TestClient(unittest.TestCase):

    def setUp(self):
        api_key = 'my-api-key'
        self.client = Client(api_key)

    def tearDown(self):
        self.client = None

    @httpretty.activate
    def test_create_bundle(self):
        register_uris(httpretty)
        bundle = self.client.create_bundle(name="test", external_id="123")
        self.assertIsNotNone(bundle)
        self.assertEqual(parse_qs(httpretty.last_request().body.decode('utf-8')),
                         {'name': ['test'], 'external_id': ['123']})

    @httpretty.activate
    def test_list_bundles(self):
        register_uris(httpretty)
        result = self.client.get_bundle_list()
        self.assertIsNotNone(result)

    @httpretty.activate
    def test_get_bundle(self):
        register_uris(httpretty)
        href = "/v1/bundles/bd9f12f93d3a4f63a89b4d249427d55f"
        result = self.client.get_bundle(href)
        self.assertIsNotNone(result)
        self.assertEqual(get_link_href(result, 'self'), href)

    @httpretty.activate
    def test_get_bundle_embedded(self):
        register_uris(httpretty)
        href = "/v1/bundles/bd9f12f93d3a4f63a89b4d249427d55f"
        result = self.client.get_bundle(href, embed_tracks=True,
                                        embed_metadata=True, embed_insights=True)
        self.assertIsNotNone(result)
        self.assertEqual(httpretty.last_request().querystring, {
            "embed": ['tracks,metadata,insights']
        })

        self.assertEqual(get_link_href(result, 'self'), href)
        tracks = get_embedded(result, 'clarify:tracks')
        self.assertIsNotNone(tracks['tracks'][0]['media_url'])
        self.assertEqual(get_link_href(tracks, 'parent'), href)
        metadata = get_embedded(result, 'clarify:metadata')
        self.assertEqual(get_link_href(metadata, 'parent'), href)
        self.assertEqual(get_link_href(metadata, 'self'), get_link_href(result, 'clarify:metadata'))
        insights = get_embedded(result, 'clarify:insights')
        self.assertEqual(get_link_href(insights, 'parent'), href)
        self.assertEqual(get_link_href(insights, 'self'), get_link_href(result, 'clarify:insights'))

    @httpretty.activate
    def test_get_tracks(self):
        register_uris(httpretty)
        href = "/v1/bundles/bd9f12f93d3a4f63a89b4d249427d55f"
        result = self.client.get_bundle(href)
        tracks_href = get_link_href(result, 'clarify:tracks')
        result = self.client.get_track_list(tracks_href)
        self.assertIsNotNone(result)
        self.assertEqual(get_link_href(result, 'self'), tracks_href)

    @httpretty.activate
    def test_get_metadata(self):
        register_uris(httpretty)
        href = "/v1/bundles/bd9f12f93d3a4f63a89b4d249427d55f"
        result = self.client.get_bundle(href)
        metadata_href = get_link_href(result, 'clarify:metadata')
        result = self.client.get_metadata(metadata_href)
        self.assertIsNotNone(result)
        self.assertEqual(get_link_href(result, 'self'), metadata_href)

    @httpretty.activate
    def test_get_insights(self):
        register_uris(httpretty)
        href = "/v1/bundles/bd9f12f93d3a4f63a89b4d249427d55f"
        result = self.client.get_bundle(href)
        insights_href = get_link_href(result, 'clarify:insights')
        result = self.client.get_insights(insights_href)
        self.assertIsNotNone(result)
        self.assertEqual(get_link_href(result, 'self'), insights_href)

    @httpretty.activate
    def test_get_insight_classification(self):
        register_uris(httpretty)
        href = "/v1/bundles/bd9f12f93d3a4f63a89b4d249427d55f"
        result = self.client.get_bundle(href)
        insights_href = get_link_href(result, 'clarify:insights')
        result = self.client.get_insights(insights_href)
        insight_href = get_link_href(result, 'insight:classification')
        result = self.client.get_insight(insight_href)
        self.assertIsNotNone(result)
        self.assertEqual(get_link_href(result, 'self'), insight_href)

    @httpretty.activate
    def test_request_insight(self):
        register_uris(httpretty)
        href = "/v1/bundles/bd9f12f93d3a4f63a89b4d249427d55f"
        result = self.client.get_bundle(href)
        insights_href = get_link_href(result, 'clarify:insights')
        result = self.client.request_insight(insights_href, 'transcript_r9')
        self.assertIsNotNone(result)
        self.assertEqual(parse_qs(httpretty.last_request().body.decode('utf-8')),
                         {'insight': ['transcript_r9']})
        self.assertEqual(get_link_href(result, 'clarify:bundle'), href)
