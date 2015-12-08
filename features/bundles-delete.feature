Feature: As a user of the API, I am able to delete a bundle.
  Scenario: A user has added a new media file for processing.
    Given I am using the environment's API key
    And I have a bundle named "K.C."
    When I delete my bundle
    Then the server should not list my bundle