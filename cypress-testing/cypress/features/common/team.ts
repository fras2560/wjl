import { Then } from 'cypress-cucumber-preprocessor/steps';

/** Assert that on a team page for some team. */
const assertTeamPage = (): void => {
    cy.get<string>('@team').then((team) => {
        cy.findByRole('heading', { name: RegExp(team, 'i') }).should('be.visible');
    });
};
Then(`I see more information about the team`, assertTeamPage);