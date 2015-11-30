Feature: As an unauthenticated user, I get an exception that I can handle.
  Scenario: I have not entered an API key, but attempt to connect anyway.
    Given I am not using an API key
    When I request a list of bundles without authentication
    Then the response should be rejected with a 401 Unauthorized status code