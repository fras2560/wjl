import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps';

/** WJL web pages that do not need identifiers. */
export type Page = 'home' | 'schedule' | 'standings' | 'submit score' | 'login' | 'edit games' | 'pending requests';

/** Navigate to a standard page of the site. */
export const visitPage = (page: Page): void => {
    const url = page.replace(' ', '_').replace('home', '');
    cy.visit(url);
};
When(`I visit the {} page`, visitPage);

/** Assert the currently on the given page */
export const assertPage = (page: Page): void => {
    const pageName = page.replace(' ', '');
    cy.findByRole('document', { name: pageName });
};
Then(`I am on the {} page`, assertPage);

/** Ensure that navigating to page and on that page. */
export const ensurePage = (page: Page): void => {
    visitPage(page);
    assertPage(page);
};
Given(`on the {} page`, ensurePage);

const accessiblePage = (): void => {
    cy.injectAxe();
    cy.configureAxe({
        reporter: 'v2',
        iframes: true,
    });
    cy.checkA11y();
};
Then(`the page is accessible`, accessiblePage);
