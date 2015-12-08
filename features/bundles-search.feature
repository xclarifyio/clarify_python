Feature: As a user of the API, I am able to search for bundles based on the content.
  Scenario: I am building a search functionality into my application.
    Given I am using the documentation API key
    And I know the following urls referenced as:
      | name                          | URL                                                                                                 |
      | media:science-of-happiness    | http://media.clarify.io/video/presentations/DanGilbert-TED2004-The-Surprising-Science-of-Happiness.mp4              |
    When I create a bundle named "Science of Happiness" with the media url "[media:science-of-happiness]"
    When I search my bundles for the text "happy" in "en"
    Then I should get the HTTP status code 200
    And My results should include a track with the URL "[media:science-of-happiness]"