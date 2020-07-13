Feature: Standings page

    The standings page gives an idea of where teams stand

Scenario: Able to view the standings page for Summer 2020
    When I visit the standings page
    Then the teams are ordered by win percentage

Scenario Outline: Able to sort by a stat category
    When I visit the standings page
    And I sort by <column>
    Then the teams are ordered by <column>

    Examples:
        |   column   |
        |    jams    |
        |    slots   |
        |    wins    |

Scenario: Able to search for a given team
    When I visit the standings page
     And I search for a team
    Then the team is visible
     And no other team is visible