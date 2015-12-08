
Feature: As a user of the API, I am able to add tracks to a bundle.
  Scenario: A user has added tracks to a bundle.
    Given I am using the environment's API key
    And I know the following urls referenced as:
      | name          | URL                                                                          |
      | media:dorothy | http://media.clarify.io/audio/books/dorothyandthewizardinoz_01_baum_64kb.mp3 |
    And I have a bundle named "Wizard of Oz"
    And My bundle should have exactly "0" tracks
    When I add a track with URL "[media:dorothy]" to the bundle
    Then I should get the HTTP status code 201
    And My bundle should have exactly "1" tracks