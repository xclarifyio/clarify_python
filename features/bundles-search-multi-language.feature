Feature: As a user of the API, I am able to search in a supported language.
  Scenario: I am using non-English media and want to search in that same language
    Given I am using the environment's API key
    And I know the following urls referenced as:
      | name                          | URL                                                                |
      | media:french-antonella-verdiani       | http://media.clarify.io/video/presentations/Antonella-Verdiani-TEDxVaugirardRoad-Eduquions-nos-enfants.mp4   |
    When I create a bundle named "Antonella Verdiani - TEDxVaugirardRoad" with the media url "[media:french-antonella-verdiani]"
    When I search my bundles for the text "musique" in "fr"
    Then I should get the HTTP status code 200
    And My results should include a track with the URL "[media:french-antonella-verdiani]"