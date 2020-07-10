/**
 * Holds a global steps and hooks.
 * @packageDocumentation
 */

/**
 * A hook that runs once before all tests. It logs out the current user
 * such that Möbius does not have them recorded as active.
 */
const globalAfter = (): void => {
    cy.request({
        url: 'logout',
        method: 'GET',
    });
    cy.log('Completed logging out');
};
afterEach(globalAfter);
