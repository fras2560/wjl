Feature: Testing the homepage

    the homepage of the site

Scenario: The homepage works as expected
    When I visit the homepage
    Then I am welcomed
     And I see option to login

Scenario: The homepage works as expected
    Given I am logged in
    When I visit the homepage
    Then I am welcomed
     And I see option to logout

Scenario: Homepage redirects to page previously accessing before logging in
    Given I am not logged in
    When I try to submit a score
     And I login
    Then I see list of games needing scores

Scenario: Homepage does not continually redirect
    Given I was redirected after logging in
    When I visit the homepage
    Then I am welcomed
