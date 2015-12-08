Feature: As a user of the API, I am able to list my submitted bundles.
  Scenario: I am building an index page to my bundle collection.
    Given I am using the environment's API key
    And I know the following urls referenced as:
      | name                          | URL                                                                |
      | media:statue-of-liberty       | http://media.clarify.io/audio/speeches/FDR-Statue-of-Liberty.mp3   |
    When I create a bundle named "Statue of Liberty" with the media url "[media:statue-of-liberty]"
    And I wait until the bundle has the "insight:spoken_words" insight
    Then The spoken words insight should reveal "765" spoken words
