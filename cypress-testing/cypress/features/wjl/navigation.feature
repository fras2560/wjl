Feature: Testing the navigation bar

    the navigation bar of the app

    Scenario: All links are visible and accessible
        When I visit the home page
        Then all standard links are visible

    Scenario: All admin links are visible and accessible
        Given I am convenor
        When I visit the home page
        Then all convenor links are visible

    Scenario Outline: All resources that are protected work and see option to login
        Given on the home page
        When I click <link>
        Then I am on the <link> page
        And I see option to login
        Examples:
            | link      |
            | home      |
            | schedule  |
            | standings |
            | videos    |

    Scenario Outline: All resources that are protected work when logged-in and see option to logout
        Given I am logged in
        And on the home page
        When I click <link>
        Then I am on the <link> page
        And I see option to logout
        Examples:
            | link      |
            | home      |
            | schedule  |
            | standings |
            | videos    |

    Scenario Outline: All private links redirect to login
        Given I am not logged in
        And on the home page
        When I click <link>
        Then I am on the login page

        Examples:
            | link  |
            | login |

    Scenario Outline: All private links work when logged in
        Given I am logged in
        And on the home page
        When I click <link>
        Then I am on the <page> page

        Examples:
            | link      | page         |
            | gamesheet | submit score |

    Scenario Outline: All admin links work when logged in as convenor
        Given I am convenor
        And on the home page
        When I click <link>
        Then I am on the <page> page

        Examples:
            | link     | page             |
            | requests | pending requests |
            | matches  | edit games       |
