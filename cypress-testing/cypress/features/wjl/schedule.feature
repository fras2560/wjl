Feature: Schedule page

    The schedule page gives information about past and future games

Scenario: Able to view the schedule page for Summer 2020
    When I visit the schedule page
    Then the schedule is displayed

Scenario: Able to search for a given team
    When I visit the schedule page
     And I search for a team
    Then can see all the team's games

Scenario: Team links work
    Given I am logged in
    When I visit the schedule page
     And I search for a team
     And click on a team link
    Then I see more information about the team

Scenario: Field links work
    Given I am logged in
    When I visit the schedule page
     And I search for a field
     And click on a field link
    Then see details about the field
