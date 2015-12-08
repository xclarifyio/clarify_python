Feature: As a user of the API, I am able to create a bundle.
  Scenario: A user has added a new media file for processing.
    Given I am using the environment's API key
    And I know the following urls referenced as:
      | name          | URL                                                                          |
      | media:dorothy | http://media.clarify.io/audio/books/dorothyandthewizardinoz_01_baum_64kb.mp3 |
    When I create a bundle named "Wizard of Oz" with the media url "[media:dorothy]"
    When I request a list of bundles
    Then I should get the HTTP status code 200
    And my results should include a bundle named "Wizard of Oz"