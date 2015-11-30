Feature: As a user of the API, I am able to get keywords for a selected media file.
  Scenario: After I upload a file, I can get the keywords back from it
    # This is not a great test, but I wanted to get *A* cuke in place before
    # releasing this test.
    Given I am using the environment's API key
    And I know the following urls referenced as:
      | name          | URL                                                                          |
      | media:dorothy | http://media.clarify.io/audio/books/dorothyandthewizardinoz_01_baum_64kb.mp3 |
    When I create a bundle named "Wizard of Oz" with the media url "[media:dorothy]"
    And I wait until the bundle has the "insight:spoken_keywords" insight
    Then I should receive "20" keywords including "dorothy"