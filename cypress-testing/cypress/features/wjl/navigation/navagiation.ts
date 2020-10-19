import { When, Then } from 'cypress-cucumber-preprocessor/steps';
import { defineParameterType } from 'cypress-cucumber-preprocessor/steps';
import { Player } from 'cypress/interfaces/player';

/** The name of the link. */
export type LinkName =
    | 'home'
    | 'login'
    | 'logout'
    | 'schedule'
    | 'standings'
    | 'gamesheet'
    | 'admin'
    | 'requests'
    | 'matches';

/** All the public standard navigation  links. */
const STANDARD_LINKS = ['home', 'schedule', 'standings', 'gamesheet'];

/** A link the requires the user to be logged in. */
const LOGGED_IN_LINKS = ['requests'];

/** The admin navigation links. */
const ADMIN_LINKS = ['matches'];

/** Defines the a gherkin parameter type called LinkName. */
defineParameterType({
    name: 'LinkName',
    regexp: RegExp('home|login|logout|schedule|standings|gamesheet|admin|requests|matches'),
    transformer: (page: string): LinkName => {
        return page.toLowerCase().replace(' ', '') as LinkName;
    },
});

/** Click admin naviation. */
const clickAdmin = (): void => {
    cy.findByRole('button', { name: /admin/i }).click();
};

/** Assert there is a way to login. */
const assertLoginOption = (): void => {
    cy.findByRole('list', { name: 'NavigationItems' }).within(() => {
        cy.findByRole('listitem', { name: /login/i }).should('be.visible');
    });
};
Then(`I see option to login`, assertLoginOption);

/** Assert there is a way to logout. */
const assertLogoutOption = (): void => {
    // assert logged in as the expected user
    cy.findByRole('list', { name: 'NavigationItems' }).within(() => {
        cy.get<Player>('@current_player').then((player) => {
            cy.findByRole('listitem', { name: /logout/i }).should('exist');
            cy.findByRole('link', { name: player.email }).should('be.visible');
        });
    });
};
Then(`I see option to logout`, assertLogoutOption);

/**
 * Gets the navigation element.
 * @param link the name of the navigation link
 * @return the navigation link
 */
const getNavigationElement = (link: LinkName): Cypress.Chainable<JQuery> => {
    if (ADMIN_LINKS.includes(link)) {
        return cy.findByRole('listitem', { name: 'Admin' }).findByRole('link', { name: RegExp(link, 'i') });
    }
    return cy.findByRole('list', { name: 'NavigationItems' }).findByRole('listitem', { name: RegExp(link, 'i') });
};

/**
 * Assert the link is visible and accessible.
 * @param link the name of the link
 */
const assertLinkVisisble = (link: LinkName): void => {
    getNavigationElement(link).should('be.visible');
};

/** Assert all the standard links are visisible. */
const assertLinksVisible = (): void => {
    for (const link of STANDARD_LINKS) {
        assertLinkVisisble(link as LinkName);
    }
};
Then(`all standard links are visible`, assertLinksVisible);

/** Assert all the convenor links are visisible. */
const assertConvenorLinks = (): void => {
    clickAdmin();
    for (const link of ADMIN_LINKS.concat(LOGGED_IN_LINKS)) {
        assertLinkVisisble(link as LinkName);
    }
};
Then(`all convenor links are visible`, assertConvenorLinks);

const clickLink = (link: LinkName): void => {
    if (ADMIN_LINKS.includes(link)) {
        clickAdmin();
    }
    getNavigationElement(link).click();
};
When(`I click {LinkName}`, clickLink);
