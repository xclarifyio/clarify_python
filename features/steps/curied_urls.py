from behave import *


class UrlTable(dict):

    def resolve(self, url):
        if url[0] == '[':
            url = self[url]
        return url


@given('I know the following urls referenced as')
def step_impl(context):
    context.url_table = UrlTable()

    for row in context.table:
        context.url_table['[' + row['name'] + ']'] = row['URL']
