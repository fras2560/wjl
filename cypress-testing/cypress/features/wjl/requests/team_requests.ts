import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps';
import { somePlayer } from '@Common/helpers';
import { createTeam, updateTeam } from '@Common/models';
import { convenorLogin } from '@Common/login';
import { TeamRequest } from '@Interfaces/teamRequest';
import { Team } from '@Interfaces/team';
import { Player } from '@Interfaces/player';

/** Some player has requested to join a team. */
const requestToJoin = (): void => {
    // create some player
    cy.login(somePlayer()).then((player) => {
        // logout as the player
        cy.wrap(player).as('playerRequest');
        cy.logout();

        // now make team
        convenorLogin();
        createTeam([], null).then((team) => {
            const request: TeamRequest = { team_id: team.id, player_id: player.id, register: true } as TeamRequest;
            cy.request({ url: '/api/team/registration', method: 'POST', body: request }).then((result) => {
                expect(result.status).to.be.eq(200);
                const resultTeam: Team = result.body as Team;
                expect(resultTeam.id).to.be.eq(team.id);
            });
            cy.wrap(team).as('teamRequest');
        });
        // logout as admin
        cy.logout();
    });
};
Given(`some player has requested to join some team`, requestToJoin);

/** Const add a player to a team. */
const addToTeam = (): void => {
    cy.login(somePlayer()).then((me) => {
        // login as some convenor
        cy.logout();
        convenorLogin();

        // now update the team to include me
        cy.get<Team>('@teamRequest').then((team) => {
            team.players.push(me);
            updateTeam(team);
        });
        // login as me again
        cy.logout();
        cy.login(me);
    });
};

Given(`I am on the team`, addToTeam);

/** Accept a request for some player. */
const acceptRequest = (): void => {
    cy.get<Player>('@playerRequest').then((player) => {
        cy.findByRole('listitem', { name: RegExp(`${player.name}`, 'i') }).within(() => {
            cy.findByRole('button', { name: /accept/i }).click();
        });
    });
};
When(`I accept the team request`, acceptRequest);

/** Assert the player who had a request is on the team. */
const assertPlayerOnTeam = (): void => {
    cy.get<Player>('@playerRequest').then((player) => {
        cy.get<Team>('@teamRequest').then((team) => {
            cy.request({ url: `api/team/${team.id}` }).then((xhr) => {
                expect(xhr.status).to.be.eq(200);
                const teamResult = xhr.body as Team;
                expect(teamResult.players).to.deep.include(player);
            });
        });
    });
};
Then(`the player is on the team`, assertPlayerOnTeam);
