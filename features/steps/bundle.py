from behave import *
import time
from clarify_python.helper import get_link_href, get_embedded


@when('I request a list of bundles without authentication')
def step_impl(context):
    try:
        context.result = context.customer.client().get_bundle_list()
    except Exception as e:
        context.exception = e


@when('I request a list of bundles')
def step_impl(context):
    context.result = context.customer.client().get_bundle_list()


@when('I create a bundle named "{name}" with the media url "{url}"')
def step_impl(context, name, url):
    name = context.names.translate(name)
    url = context.url_table.resolve(url)
    try:
        context.my_bundle = context.customer.client().create_bundle(name=name, media_url=url)
    except Exception as e:
        print(e)


@then('my results should include a bundle named "{name}"')
def step_impl(context, name):
    found = False
    bundle_name = context.names.translate(name)

    def check_bundle_name(client, bundle_href):
        nonlocal found, bundle_name

        bundle = client.get_bundle(bundle_href)
        if bundle['name'] == bundle_name:
            found = True
            return False

    context.customer.client().bundle_list_map(check_bundle_name, context.result)
    assert found


@given('I have a bundle named "{name}"')
def step_impl(context, name):
    name = context.names.translate(name)
    context.my_bundle = context.customer.client().create_bundle(name=name)


@when('I delete my bundle')
def step_impl(context):
    context.customer.client().delete_bundle(get_link_href(context.my_bundle, 'self'))


@then('the server should not list my bundle')
def step_impl(context):
    found = False
    my_bundle_href = get_link_href(context.my_bundle, 'self')

    def check_bundle_href(client, bundle_href):
        nonlocal my_bundle_href, found
        if bundle_href == my_bundle_href:
            found = True

    context.customer.client().bundle_list_map(check_bundle_href)
    assert not found


@then('My results should include a track with the URL "{url}"')
def step_impl(context, url):
    found = False
    url = context.url_table.resolve(url)

    def check_bundle_track(client, bundle_href):
        nonlocal found, url

        bundle = client.get_bundle(bundle_href, embed_tracks=True)
        tracks = get_embedded(bundle, 'clarify:tracks')
        for track in tracks['tracks']:
            if track['media_url'] == url:
                found = True
                return False

    context.customer.client().bundle_list_map(check_bundle_track, context.result)
    assert found


@when('I search my bundles for the text "{text}" in "{lang}"')
def step_impl(context, text, lang):
    # Wait for the bundle to be indexed
    time.sleep(4)
    context.result = context.customer.client().search(query=text, language=lang)


@when('I wait until the bundle has the "{insight_rel}" insight')
def step_impl(context, insight_rel):
    keywords_href = None
    while keywords_href is None:
        insights = context.customer.client().get_bundle(get_link_href(context.my_bundle, 'clarify:insights'))
        keywords_href = get_link_href(insights, insight_rel)
        if keywords_href is None:
            time.sleep(3)


@then('I should receive "{count:d}" keywords including "{word}"')
def step_impl(context, count, word):
    insights = context.customer.client().get_insights(get_link_href(context.my_bundle, 'clarify:insights'))
    keywords = context.customer.client().get_insight(get_link_href(insights, 'insight:spoken_keywords'))

    found = False
    for kw in keywords['track_data'][0]['keywords']:
        if kw['term'] == word:
            found = True
            break

    assert len(keywords['track_data'][0]['keywords']) == count
    assert found


@then('The spoken words insight should reveal "{count:d}" spoken words')
def step_impl(context, count):
    insights = context.customer.client().get_insights(get_link_href(context.my_bundle, 'clarify:insights'))
    spoken_words = context.customer.client().get_bundle(get_link_href(insights, 'insight:spoken_words'))
    assert spoken_words['track_data'][0]['word_count'] == count


@given('My bundle should have exactly "{count:d}" tracks')
def step_impl(context, count):
    tracks = context.customer.client().get_track_list(get_link_href(context.my_bundle, 'clarify:tracks'))
    assert len(tracks['tracks']) == count


@then('My bundle should have exactly "{count:d}" tracks')
def step_impl(context, count):
    tracks = context.customer.client().get_track_list(get_link_href(context.my_bundle, 'clarify:tracks'))
    assert len(tracks['tracks']) == count


@when('I add a track with URL "{url}" to the bundle')
def step_impl(context, url):
    url = context.url_table.resolve(url)
    context.customer.client().create_track(get_link_href(context.my_bundle, 'clarify:tracks'), media_url=url)


@given('I add a track with URL "{url}" to the bundle')
def step_impl(context, url):
    url = context.url_table.resolve(url)
    context.customer.client().create_track(get_link_href(context.my_bundle, 'clarify:tracks'), media_url=url)


@when('I request a list of tracks')
def step_impl(context):
    context.my_tracks = context.customer.client().get_track_list(get_link_href(context.my_bundle, 'clarify:tracks'))


@then('my tracks should include the URL "{url}"')
def step_impl(context, url):
    found = False
    url = context.url_table.resolve(url)

    for track in context.my_tracks['tracks']:
        if track['media_url'] == url:
            found = True
            break
    assert found
