Feature: Team feature

    Tests the team page

Scenario: Anonymous cannot view team
    Given a team exists
     And I am not logged in
    When I try to access the team
    Then I am on the login page

@focus
Scenario: Players can view other teams
    Given a team exists
     And I am logged in
    When I try to access the team
    Then see details about the team
