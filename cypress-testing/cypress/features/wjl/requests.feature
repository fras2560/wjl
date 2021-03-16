Feature: Team requests

  Convenors or team mates can respond to requests to join Team

  Scenario: The requests page meets accessibility standards
    Given some player has requested to join some team
    And I am convenor
    And on the pending requests page
    Then the page is accessible

  Scenario: Convenor able to accept a request
    Given some player has requested to join some team
    And I am convenor
    And on the pending requests page
    When I accept the team request
    Then the player is on the team

  Scenario: Team member able to accept the requests as well
    Given some player has requested to join some team
    And I am on the team
    And on the pending requests page
    When I accept the team request
    Then the player is on the team

