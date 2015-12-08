
Feature: As a user of the API, I am able to get all of my tracks for a bundle.
  Scenario: A user wants a list of their tracks for a bundle.
    Given I am using the environment's API key
    And I know the following urls referenced as:
      | name          | URL                                                                          |
      | media:dorothy | http://media.clarify.io/audio/books/dorothyandthewizardinoz_01_baum_64kb.mp3 |
      | media:dorothy2 | http://media.clarify.io/audio/books/dorothyandthewizardinoz_01_baum_64kb.mp3 |
    And I have a bundle named "Wizard of Oz"
    And I add a track with URL "[media:dorothy]" to the bundle
    And I add a track with URL "[media:dorothy2]" to the bundle
    When I request a list of tracks
    Then my tracks should include the URL "[media:dorothy]"
    And my tracks should include the URL "[media:dorothy2]"