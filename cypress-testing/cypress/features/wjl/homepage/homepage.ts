import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps';
import { login } from '@Common/login';
import { Player } from '@Models/player';

/** Navigate to the homepage of the site. */
const visitHomepage = (): void => {
    cy.visit('');
};
When(`I visit the homepage`, visitHomepage);

/** Navigate to the submit score page. */
const visitSubmitScorePage = (): void => {
    cy.visit('submit_score');
};
When(`I try to submit a score`, visitSubmitScorePage);

/** Assert I am on the welcome page. */
const welcomed = (): void => {
    cy.findByRole('heading', { name: /welcome/i }).should('be.visible');
};
Then(`I am welcomed`, welcomed);

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

/** Assert on the submit score page. */
const assertOnSubmitScoresPage = (): void => {
    // just check document type
    // other tests will double check the page structure
    cy.findByRole('document', { name: /submitscore/i });
};
Then(`I see list of games needing scores`, assertOnSubmitScoresPage);

/** Access some resource and then login */
const accessResourceAndLogin = (): void => {
    visitSubmitScorePage();
    login();
    assertOnSubmitScoresPage();
};
Given(`I was redirected after logging in`, accessResourceAndLogin);
