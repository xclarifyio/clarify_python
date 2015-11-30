import os
import re
import uuid
from clarify_python.clarify import Client


class Customer(object):
    """Manage creating the client using different keys"""

    def __init__(self):
        self._client = None
        self.api_key = ''

    def log_in_as_docs(self):
        self._set_api_key('docs-api-key')

    def log_in_via_environment(self):
        self._set_api_key(os.environ.get('CLARIFY_API_KEY'))

    def clear_api_key(self):
        self._set_api_key('')

    def _set_api_key(self, val):
        self.api_key = val
        self._client = None

    def client(self):
        if not self._client:
            self._client = Client(self.api_key)
        return self._client


class Names(object):
    """Take names you use in a test and make them unique, guaranteeing two tests
    can't trample on the same account."""

    def __init__(self):
        self.uuid = str(uuid.uuid4())

    def translate(self, name):
        return "{0}_{1}".format(self.uuid, name)

    def matches(self, name):
        return re.compile("^{0}_(.*)".format(re.escape(self.uuid))).match(name) is not None


def before_all(context):
    context.customer = Customer()
    context.names = Names()


def after_all(context):
    context.customer.log_in_via_environment()

    def _delete_test_bundle(client, bundle_href):
        nonlocal context
        bundle = client.get_bundle(bundle_href)
        if context.names.matches(bundle['name']):
            client.delete_bundle(bundle_href)

    context.customer.client().bundle_list_map(_delete_test_bundle)
    context.customer = None


def before_scenario(context, scenario):
    context.exception = None
    context.result = None
    context.my_bundle = None
    context.my_tracks = None
