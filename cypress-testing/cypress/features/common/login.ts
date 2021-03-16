import { Given, When } from 'cypress-cucumber-preprocessor/steps';
import { somePlayer } from '@Common/helpers';

/** A function that logs in the user. */
export const login = (): void => {
    const player = somePlayer();
    cy.login(player).then((player) => {
        cy.wrap(player).as('current_player');
        cy.visit('');
    });
};
Given('I am logged in', login);
When('I login', login);

/** A function that logs as an convenor. */
export const convenorLogin = (): void => {
    const player = somePlayer();
    player.is_convenor = true;
    cy.login(player).then((player) => {
        cy.wrap(player).as('current_player');
        cy.visit('');
    });
};
Given('I am convenor', convenorLogin);

/** A unfciton the guarantees currently logged out */
const loggedOut = (): void => {
    cy.clearCookies();
};

Given('I am not logged in', loggedOut);
