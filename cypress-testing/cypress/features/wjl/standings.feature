Feature: Standings page

    The standings page gives an idea of where teams stand

Scenario: Able to view the standings page for Summer 2020
    Given there is a league session 
     And my team is first in the place
    When I visit the standings page
    Then I see my team at the top of the standings

