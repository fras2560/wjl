import { When, Then } from 'cypress-cucumber-preprocessor/steps';
import { defineParameterType } from 'cypress-cucumber-preprocessor/steps';
import { Player } from '@Models/player';

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
const standardLinks = ['home', 'schedule', 'standings', 'gamesheet'];

/** The admin navigation links. */
const adminLinks = ['requests', 'matches'];

/** Defines the a gherkin parameter type called Role. */
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
 * Assert the link is visible and accessible.
 * @param link the name of the link
 */
const assertLinkVisisble = (link: LinkName): void => {
    cy.findByRole('list', { name: 'NavigationItems' }).within(() => {
        cy.findByRole('listitem', { name: RegExp(link, 'i') }).should('be.visible');
    });
};

/** Assert all the standard links are visisible. */
const assertLinksVisible = (): void => {
    for (const link of standardLinks) {
        assertLinkVisisble(link as LinkName);
    }
};
Then(`all standard links are visible`, assertLinksVisible);

/** Assert all the convenor links are visisible. */
const assertConvenorLinks = (): void => {
    clickAdmin();
    for (const link of adminLinks) {
        assertLinkVisisble(link as LinkName);
    }
};
Then(`all convenor links are visible`, assertConvenorLinks);

const clickLink = (link: LinkName): void => {
    if (adminLinks.includes(link)) {
        clickAdmin();
    }
    cy.findByRole('list', { name: 'NavigationItems' }).within(() => {
        cy.findByRole('listitem', { name: RegExp(link, 'i') }).click();
    });
};
When(`I click {LinkName}`, clickLink);
