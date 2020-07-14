Feature: Score app

    App that allows people to keep track of stats for each game and then submit the score

# The background for the score app will setup

Scenario Outline: Negative points for going over 21
    Given I am convenor
      And there is a game today
      And using the score App
      And home team score is <starting_score>
    When home team gets a <action>
    Then home team score becomes <resulting_score>

    Examples:
    |starting_score|  action  | resulting_score |
    |      20      |   jam    |       17        |
    |      20      |  deuce   |       18        |
    |      19      |   jam    |       16        |
