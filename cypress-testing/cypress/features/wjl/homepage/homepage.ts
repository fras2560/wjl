import { When, Then } from 'cypress-cucumber-preprocessor/steps';

/** Navigate to the homepage of the site. */
const visitHomepage = (): void => {
    cy.visit("");
};
When(`I visit the homepage`, visitHomepage);


/** Assert I am on the welcome page. */
const welcomed = (): void => {
    cy.get("[data-cy=welcomeHeader]").should("be.visible");
    cy.get("[data-cy=welcomeMessage]").should("be.visible");
};
Then(`I am welcomed`, welcomed);


/** Assert there is a way to login. */
const assertLoginOption = (): void => {
    cy.get('[data-cy=login]').should("be.visible");
};
Then(`I see option to login`, assertLoginOption);

/** Assert there is a way to logout. */
const assertLogoutOption = (): void => {
    cy.get('[data-cy=logout]').should("be.visible");
};
Then(`I see option to logout`, assertLogoutOption);