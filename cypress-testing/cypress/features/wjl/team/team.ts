import { When, Then, defineParameterType, Given } from 'cypress-cucumber-preprocessor/steps';
import { Team } from '@Interfaces/team';
import { Player } from '@Interfaces/player';
import { createTeam } from '@Common/models';
import { convenorLogin } from '@Common/login';
import { somePlayer } from '@Common/helpers';

/** Defines the a gherkin parameter type called LeaveOrJoinWhichTeam. */
defineParameterType({
    name: 'LeaveOrJoin',
    regexp: RegExp('join|leave'),
    transformer: (method: string): boolean => {
        return method.toLowerCase().trim() == 'join';
    },
});

/** Defines the a gherkin parameter type called WhichTeam. */
defineParameterType({
    name: 'OnOrOffTeam',
    regexp: RegExp('part of|not on'),
    transformer: (method: string): boolean => {
        return method.toLowerCase().trim() == 'on';
    },
});

/** Create a team and ensure current user part of team. */
const addPlayerToSomeTeam = (): void => {
    convenorLogin();
    const player = somePlayer();
    createTeam([player], null);
    cy.logout();
    cy.login(player);
};
Given(`I am part of some team`, addPlayerToSomeTeam);

/** Try to access the team by using a direct link. */
const accessTeam = (): void => {
    cy.get<Team>('@team').then((team) => {
        cy.visit(`team/${team.id}`);
    });
};
When(`I try to access the team`, accessTeam);

/**
 * Change one's registration with a team.
 * @param status whether to join the team or leave the team
 */
const changeTeamRegistration = (status: boolean): void => {
    if (status) {
        cy.findByRole('button', { name: /join/i }).click();
    } else {
        cy.findByRole('button', { name: /leave/i }).click();
    }
};
When(`request to {LeaveOrJoin} the team`, changeTeamRegistration);

/**
 * Assert the current status for a given team.
 * @param status whether expecting to be on the team or not
 */
const assertTeamStatus = (status: boolean): void => {
    cy.get<Team>('@team').then((team) => {
        cy.get<Player>('@current_player').then((player) => {
            cy.request({
                method: 'GET',
                url: `api/team/${team.id}`,
            }).then((xhr) => {
                const team = xhr.body as Team;
                if (status) {
                    expect(team.players).to.deep.include(player);
                } else {
                    expect(team.players).to.not.deep.include(player);
                }
            });
        });
    });
};
Then(`I am {OnOrOffTeam} the team`, assertTeamStatus);

/** Asserting that have a pending requests to join a team*/
const assertPendingRequest = (): void => {
    cy.findByRole('main', { name: /main-content/i }).within(() => {
        cy.contains(/request.*pending/i);
    });
};
Then(`my request is pending`, assertPendingRequest);
