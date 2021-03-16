Feature: Testing the homepage

    the homepage of the site

    Scenario: The homepage meets accessibility standards
        When I visit the home page
        Then the page is accessible

    Scenario: The homepage works as expected
        When I visit the home page
        Then I am welcomed

    Scenario: The homepage works as expected
        Given I am logged in
        When I visit the home page
        Then I am welcomed

    Scenario: Homepage redirects to page previously accessing before logging in
        Given I am not logged in
        When I visit the submit score page
        And I login
        Then I am on the submit score page

    Scenario: Homepage does not continually redirect
        Given I was redirected after logging in
        When I visit the home page
        Then I am welcomed
