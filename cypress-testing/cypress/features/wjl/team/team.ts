import { When } from 'cypress-cucumber-preprocessor/steps';
import { Team } from '@Interfaces/team';

/** Try to access the team by using a direct link. */
const accessTeam = (): void => {
    cy.get<Team>('@team').then((team) => {
        cy.visit(`team/${team.id}`);
    });
};
When(`I try to access the team`, accessTeam);
