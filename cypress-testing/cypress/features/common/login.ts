import { Given } from 'cypress-cucumber-preprocessor/steps';
import { Player } from '@Models/player';
import uuidv4 from 'uuid/v4';

/**
 * Creates a random name to use for testing.
 * @return a random name
 * @example
 * ```typescript
 * const firstName = randomName();
 * ```
 */
export function randomName(): string {
    return uuidv4().split('-')[0];
}

/**
 * Creates a random email to use for testing.
 * @return a random email with domain of @digitalEducationTesting
 * @example
 * ```typescript
 * const email = randomEmail();
 * ```
 */
export function randomEmail(): string {
    return randomName() + '-' + randomName() + '@wjl.ca';
}

const login = (): void => {
    const player = new Player(randomEmail(), randomName())
    cy.login(player);
    cy.wrap(player).as("current_player");
};

Given("I am logged in", login);