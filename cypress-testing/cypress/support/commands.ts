/* eslint-disable @typescript-eslint/no-explicit-any */
/**
 * Some custom commands for Möbius. See
 * {@link https://docs.cypress.io/api/cypress-api/custom-commands.html | custom commands}
 * for more details on creating custom commands and
 * over riding default commands.
 * Some best practices to follow:
 * <ul>
 *    <li> DO NOT make everything a custom command</li>
 *    <li> DO NOT overcomplicate things</li>
 *    <li> DO NOT do too much in a single command</li>
 *    <li> DO skip the UI as much as possible </li>
 * </ul>
 * @packageDocumentation
 */

import { Player } from 'cypress/interfaces/player';
import '@testing-library/cypress/add-commands';

/**
 * Logout the user.
 * @example
 * ```
 * // Logout the current user
 * cy.logout();
 * ```
 */
const logout = (): void => {
    // clear the cookies to act as if logged out
    cy.request({
        url: 'logout',
        method: 'GET',
    });
};
Cypress.Commands.add('logout', logout);

/**
 * Login the user.
 * @example
 * ```
 * // Logout the current user
 * cy.login(new Player("someEmail@wjl.ca", "name"));
 * ```
 */
const login = (player: Player): void => {
    // clear the cookies to act as if logged out
    cy.request({
        url: 'testing/api/create_and_login',
        method: 'POST',
        body: player,
    });
};
Cypress.Commands.add('login', login);
