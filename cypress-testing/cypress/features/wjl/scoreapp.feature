Feature: Score app

  App that allows people to keep track of stats for each game and then submit the score

  Scenario Outline: Game over when team hits slot
    Given I am convenor
    And there is a game today
    And using the score App
    When <team> team gets a slot
    Then <team> team score becomes 21
    And both team controls are disabled
    And able to submit the gamesheet

    Examples:
      | team |
      | home |
      | away |

  Scenario Outline: Negative points for going over 21
    Given I am convenor
    And there is a game today
    And using the score App
    And <team> team score is <starting_score>
    When <team> team gets a <action>
    Then <team> team score becomes <resulting_score>

    Examples:
      | team | starting_score | action | resulting_score |
      | home | 20             | jam    | 17              |
      | home | 20             | deuce  | 18              |
      | home | 19             | jam    | 16              |
      | away | 20             | jam    | 17              |
      | away | 20             | deuce  | 18              |
      | away | 19             | jam    | 16              |

  Scenario Outline: Able to submit once a team reaches 21
    Given I am convenor
    And there is a game today
    And using the score App
    When <team> team score is 21
    Then able to submit the gamesheet
    And <team> team controls are disabled

    Examples:
      | team |
      | home |
      | away |

  Scenario Outline: Able to select one of the overtime options
    Given I am convenor
    And there is a game today
    And using the score App
    And both teams score are 21
    And overtime options are visible
    When <method> overtime method is selected
    Then the app is using <method> method
    And both team controls are enabled

    Examples:
      | method       |
      | first to ten |
      | sudden death |

  Scenario: Able to swtich the hammer for a given game
    Given I am convenor
    And there is a game today
    And using the score App
    When the hammer is pressed
    Then away team has the hammer

  Scenario: Team with hammer can still throw if other team got to 21
    Given I am convenor
    And there is a game today
    And using the score App
    When away team score is 21
    Then away team controls are disabled
    And home team controls are enabled

  # this test could be cleaned up to be worded a bit better
  Scenario: First to ten Overtime ends when hammer team reach 31
    Given I am convenor
    And there is a game today
    And using the score App
    And both teams score are 21
    And first to ten overtime method is selected
    When home team gets a jam
    And home team gets a jam
    And home team gets a jam
    And home team gets a dinger
    Then both team controls are disabled
    And able to submit the gamesheet

  Scenario: Ensure the gamesheet is successful saved upon submission
    Given I am convenor
    And there is a game today
    And using the score App
    And home team score is 21
    And able to submit the gamesheet
    When the gamesheet is submitted
    Then gamesheet is saved
    And the app resets for next game

  Scenario: The score app meets accessibility standards
    Given I am convenor
    And there is a game today
    And using the score App
    Then the page is accessible