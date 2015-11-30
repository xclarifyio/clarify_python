from behave import *


@given('I am using the documentation API key')
def step_impl(context):
    context.customer.log_in_as_docs()


@given('I am not using an API key')
def step_impl(context):
    context.customer.clear_api_key()


@given('I am using the environment\'s API key')
def step_impl(context):
    context.customer.log_in_via_environment()
