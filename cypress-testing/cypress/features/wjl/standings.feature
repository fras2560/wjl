Feature: Standings page

    The standings page gives an idea of where teams stand

Scenario: Able to view the standings page for Summer 2020
    When I visit the standings page
    Then the teams are ordered by win percentage


