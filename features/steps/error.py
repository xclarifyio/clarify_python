from behave import *
from clarify_python.clarify import APIException


@then('the response should be rejected with a 401 Unauthorized status code')
def step_impl(context):
    assert isinstance(context.exception, APIException)
    assert context.exception.get_code() == 401
