import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps';
import { defineParameterType } from 'cypress-cucumber-preprocessor/steps';

/** WJL web pages that do not need identifiers. */
export type Page = 'home' | 'schedule' | 'standings' | 'submit score' | 'login' | 'edit games' | 'pending requests';

/** Defines the a gherkin parameter type called Role. */
defineParameterType({
    name: 'Page',
    regexp: RegExp('home|schedule|standings|submit score|login|edit games|pending requests'),
    transformer: (page: string): Page => {
        return page.toLowerCase() as Page;
    },
});

/** Navigate to a standard page of the site. */
export const visitPage = (page: Page): void => {
    const url = page.replace(' ', '_').replace('home', '');
    cy.visit(url);
};
When(`I visit the {Page} page`, visitPage);

/** Assert the currently on the given page */
export const assertPage = (page: Page): void => {
    const pageName = page.replace(' ', '');
    cy.findByRole('document', { name: pageName });
};
Then(`I am on the {Page} page`, assertPage);

/** Ensure that navigating to page and on that page. */
export const ensurePage = (page: Page): void => {
    visitPage(page);
    assertPage(page);
};
Given(`on the {Page} page`, ensurePage);
