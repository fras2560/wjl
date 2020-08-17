Feature: Team feature

    Tests the team page

Scenario: Anonymous cannot view team
    Given a team exists
     And I am not logged in
    When I try to access the team
    Then I am on the login page

Scenario: Players can view other teams and the page is accessible
    Given a team exists
     And I am logged in
    When I try to access the team
    Then see details about the team
     And the page is accessible

Scenario: Able to make a request to join a team
    Given a team exists
      And I am logged in
     When I try to access the team
      And request to join the team
     Then my request is pending

Scenario: Able to leave a team
    Given I am part of some team
     When I try to access the team
      And request to leave the team
     Then I am not on the team
