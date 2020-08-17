Feature: Field feature

    Tests the field page

Scenario: Anonymous cannot view fields
    Given a field exists
     And I am not logged in
    When I try to access the field
    Then I am on the login page

Scenario: Players can view field details and the page is accesible
    Given a field exists
     And I am logged in
    When I try to access the field
    Then see details about the field
     And the page is accessible
