/* eslint-disable @typescript-eslint/camelcase */
import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps';
import { Player } from '@Interfaces/player';
import { Team } from '@Interfaces/team';
import { Field } from '@Interfaces/field';
import { SessionInterface } from '@Interfaces/session';
import { Sheet } from '@Interfaces/sheet';
import { Match } from '@Interfaces/match';
import { randomName } from '@Common/login';
import { createField, createSession } from '@Common/models';
import { defineParameterType } from 'cypress-cucumber-preprocessor/steps';

/** Which team are we talking about. */
type WhichTeam = 'home' | 'away';

/** Defines the a gherkin parameter type called Role. */
defineParameterType({
    name: 'WhichTeam',
    regexp: RegExp('home|away'),
    transformer: (team: string): WhichTeam => {
        return team.toLowerCase().replace(' ', '') as WhichTeam;
    },
});

/** The actions that can occur */
type Action = 'jam' | 'dinger' | 'deuce' | 'slot';

/** Defines the a gherkin parameter type called Role. */
defineParameterType({
    name: 'Action',
    regexp: RegExp('jam|dinger|deuce|slot'),
    transformer: (action: string): Action => {
        return action.toLowerCase().replace(' ', '').trim() as Action;
    },
});

/**
 * Save a match between two teams that takes place today.
 * @param homeTeam the home team
 * @param awayTeam  the away team
 * @param session  the session that match occurs in
 * @param field the field the match is played on
 * @return the wrap match
 */
const saveMatch = (
    homeTeam: Team,
    awayTeam: Team,
    session: SessionInterface,
    field: Field,
): Cypress.Chainable<Match> => {
    const matchTime = new Date().toISOString().slice(0, 10);
    const match: Match = {
        home_team: homeTeam.name,
        home_team_id: homeTeam.id,
        away_team: awayTeam.name,
        away_team_id: awayTeam.id,
        field: field.name,
        field_id: field.id,
        date: matchTime,
        time: '18:00',
        datetime: `${matchTime} 18:00`,
        session: session.name,
        session_id: session.id,
        id: null,
        status: 'Testing match',
    };
    cy.request({
        url: '/api/match/save',
        method: 'POST',
        body: match,
    }).then((xhr) => {
        const match: Match = xhr.body;
        expect(session).to.have.property('id');
        cy.wrap(match).as('match');
    });
    return cy.get<Match>('@match');
};

/**
 * Save a team with name and players.
 * @param name the name of the team
 * @param players a list of players
 * @param alias the alias to wrap save team as
 * @return the wrapped team
 */
const saveTeam = (name: string, players: Array<Player>, alias: string): Cypress.Chainable<JQuery<HTMLElement>> => {
    const team: Team = { id: null, name: name, homefield: null, players: players };
    cy.request({
        url: 'api/team/save',
        method: 'POST',
        body: team,
    }).then((xhr) => {
        const team = xhr.body;
        expect(team).to.have.property('name', name);
        cy.wrap(team).as(alias);
    });
    return cy.get(`@${alias}`);
};

/** A step to setup a match between two teams. */
const setupTeamWithMatch = (): void => {
    createSession().then((session) => {
        createField().then((field) => {
            cy.get<Player>('@player').then((player) => {
                saveTeam(`My Team ${randomName()}`, [player], 'myteam');
                saveTeam(`Other Team ${randomName()}`, [], 'otherteam');
                cy.get<Team>('@myteam').then((myTeam) => {
                    cy.get<Team>('@otherteam').then((otherTeam) => {
                        saveMatch(myTeam, otherTeam, session, field);
                    });
                });
            });
        });
    });
};
Given(`there is a game today`, setupTeamWithMatch);

/** A step visit score app to setup a match between two teams. */
const visitScoreApp = (): void => {
    cy.get<Match>('@match').then((match) => {
        cy.visit(`submit_sheet/${match.id}`);
        cy.window().its('appReady').should('be.true');
        cy.window().its('scoreApp').should('exist');
    });
};
Given(`using the score App`, visitScoreApp);

/** Set the score for the given team. */
const setScore = (team: WhichTeam, score: number): void => {
    // reset the game
    cy.window().its('scoreApp').invoke('reset');
    cy.get<Match>('@match').then((match) => {
        // get the match and set the score by adding 1 until get to the score
        let i  = 0;
        let team_id = team == 'home' ? match.home_team_id : match.away_team_id;
        while (i < score) {
            cy.window().its('scoreApp').invoke('addScore', team_id, 1);
            i += 1;
        }
    });
};
Given(`{WhichTeam} team score is {int}`, setScore);

const commitAction = (team: WhichTeam, action: Action) => {
    cy.findByRole('button', {name: RegExp(`${team}.*${action}`, 'i')}).click();
}
When(`{WhichTeam} team gets a {Action}`, commitAction);

const assertTeamScore = (team: WhichTeam, score: number) => {
    if (team == "home") {
        cy.get('[data-cy=homeScore]').contains(score);
    } else {
        cy.get('[data-cy=awayScore]').contains(score);
    }
}
Then(`{WhichTeam} team score becomes {int}`, assertTeamScore);