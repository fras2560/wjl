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

/** Interface for a node in Axe model. */
interface AxeNode {
    impact: null | string;
    html: string;
}

/** An Axe rule that been verified or violated. */
interface AxeRule {
    id: string;
    nodes: Array<AxeNode>;
    impact: string;
    tags: Array<string>;
    description: string;
    help: string;
    helpUrl: string;
}

/** Axe model for reporting. */
interface Axe {
    violations: Array<AxeRule>;
    passes: Array<AxeRule>;
    testEngine: {
        name: string;
        version: string;
    };
    testRunner: {
        name: string;
    };
    testEnvironment: {
        userAgent: string;
        windowWidth: number;
        windowHeight: number;
        orientationAngle: 0;
        orientationType: 'landscape-primary';
    };
    toolOptions: {
        reprort: 'v1' | 'v2';
    };
    length: number;
}
/**
 * Logs any accessibility issues to the terminal.
 *
 * @param axe the axe run information
 */
const customViolationLogger = (axe: Axe): void => {
    const violationData = axe.violations.map(({ id, impact, description, nodes }) => ({
        id,
        impact,
        description,
        nodes: nodes.length,
    }));
    if (violationData.length > 0) {
        cy.task('table', violationData);
    }
};

/** Checks whether the page is accessible or not. */
const accessiblePage = (): void => {
    cy.injectAxe();
    cy.configureAxe({
        reporter: 'v2',
        iframes: true,
    });
    cy.checkA11y(undefined, undefined, {
        logger: customViolationLogger,
    });
};
Then(`the page is accessible`, accessiblePage);
