import { Given, Then } from 'cypress-cucumber-preprocessor/steps';
import { visitPage, assertPage } from '@Common/page';
import { login } from '@Common/login';

/** Assert I am on the welcome page. */
const welcomed = (): void => {
    cy.findByRole('heading', { name: /welcome/i }).should('be.visible');
};
Then(`I am welcomed`, welcomed);

/** Assert on the submit score page. */
const assertOnSubmitScoresPage = (): void => {
    assertPage('submit score');
};
Then(`I see list of games needing scores`, assertOnSubmitScoresPage);

/** Access some resource and then login */
const accessResourceAndLogin = (): void => {
    visitPage('submit score');
    login();
    assertOnSubmitScoresPage();
};
Given(`I was redirected after logging in`, accessResourceAndLogin);
