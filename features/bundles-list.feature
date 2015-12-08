Feature: As a user of the API, I am able to list my submitted bundles.
  Scenario: I am building an index page to my bundle collection.
    Given I am using the documentation API key
    And I know the following urls referenced as:
      | name                          | URL                                                                                                                 |
      | media:science-of-happiness    | http://media.clarify.io/video/presentations/DanGilbert-TED2004-The-Surprising-Science-of-Happiness.mp4              |
      | media:mlk-I-have-a-dream      | http://media.clarify.io/audio/speeches/MLK-I-Have-a-Dream.mp3                                                       |
      | media:fdr-statue-of-liberty   | http://media.clarify.io/audio/speeches/FDR-Statue-of-Liberty.mp3                                                    |
    When I request a list of bundles
    Then I should get the HTTP status code 200
    And My results should include a track with the URL "[media:science-of-happiness]"
    And My results should include a track with the URL "[media:mlk-I-have-a-dream]"
    And My results should include a track with the URL "[media:fdr-statue-of-liberty]"