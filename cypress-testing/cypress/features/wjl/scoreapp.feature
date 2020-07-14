Feature: Score app

    App that allows people to keep track of stats for each game and then submit the score

# The background for the score app will setup

Scenario Outline: Negative points for going over 21
    Given I am convenor
      And there is a game today
      And using the score App
      And <team> team score is <starting_score>
    When <team> team gets a <action>
    Then <team> team score becomes <resulting_score>

    Examples:
    | team |starting_score|  action  | resulting_score |
    | home |      20      |   jam    |       17        |
    | home |      20      |  deuce   |       18        |
    | home |      19      |   jam    |       16        |
    | away |      20      |   jam    |       17        |
    | away |      20      |  deuce   |       18        |
    | away |      19      |   jam    |       16        |
