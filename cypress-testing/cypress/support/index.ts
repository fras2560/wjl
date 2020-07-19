/* eslint-disable @typescript-eslint/camelcase */
/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/no-namespace */
// ***********************************************************
// This example support/index.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands';
import 'cypress-pipe';
import { Player } from '@Interfaces/player';

declare global {
    namespace Cypress {
        interface Chainable {
            /**
             * Logout a the user.
             *
             * @example
             * ```
             * // Logout the current user
             * cy.logout();
             * ```
             */
            logout(): void;
            login(player: Player): void;
        }
    }
}

// this prevents cypress from failing on javascript errors
// Möbius currently has alot
Cypress.on('uncaught:exception', () => {
    return false;
});
