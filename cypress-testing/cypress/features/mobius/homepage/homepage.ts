import { When, Then } from 'cypress-cucumber-preprocessor/steps';

/**
 * Navigate to the homepage of the site
 * @example
 * ```
 * Given I visit the homepage
 * ```
 */
const visitHomepage = (): void => {
    cy.visit("");
};
When(`I visit the homepage`, visitHomepage);


/**
 * Assert I am on the welcome page.
 * @example
 * ```
 * Then I am welcomed
 * ```
 */
const welcomed = (): void => {
    cy.get("[data-cy=welcomeHeader]").should("be.visible");
    cy.get("[data-cy=welcomeMessage]").should("be.visible");
};
Then(`I am welcomed`, welcomed);