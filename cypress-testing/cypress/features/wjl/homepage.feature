Feature: Testing the homepage

    the homepage of the site

Scenario: The homepage works as expected
    When I visit the homepage
    Then I am welcomed

@focus
Scenario: The homepage works as expected
    Given I am logged in
    When I visit the homepage
    Then I am welcomed
