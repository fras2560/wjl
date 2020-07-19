/* eslint-disable @typescript-eslint/camelcase */
import { Given, When } from 'cypress-cucumber-preprocessor/steps';
import { randomEmail, randomName } from './helpers';

/** A function that logs in the user. */
export const login = (): void => {
    const player = { email: randomEmail(), name: randomName(), is_convenor: false, id: null };
    cy.login(player);
    cy.wrap(player).as('current_player');
    cy.visit('');
};
Given('I am logged in', login);
When('I login', login);

/** A function that logs as an convenor. */
export const convenorLogin = (): void => {
    const player = { email: randomEmail(), name: randomName(), is_convenor: true, id: null };
    cy.login(player);
    cy.wrap(player).as('current_player');
    cy.visit('');
};
Given('I am convenor', convenorLogin);

/** A unfciton the guarantees currently logged out */
const loggedOut = (): void => {
    cy.clearCookies();
};

Given('I am not logged in', loggedOut);
