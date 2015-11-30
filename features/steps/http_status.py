from behave import *


@then('I should get the HTTP status code {code:d}')
def step_impl(context, code):
    assert context.customer.client().get_last_status() == code
