import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps';
import { Player } from '@Interfaces/player';
import { Team } from '@Interfaces/team';
import { Field } from '@Interfaces/field';
import { SessionInterface } from '@Interfaces/session';
import { Sheet } from '@Interfaces/sheet';
import { Match } from '@Interfaces/match';
import { randomName } from '@Common/helpers';
import { createField, createSession } from '@Common/models';
import { defineParameterType } from 'cypress-cucumber-preprocessor/steps';

/** The actions that can occur */
type Action = 'jam' | 'dinger' | 'deuce' | 'slot';

/** A list of all actions. */
const ACTIONS: Array<Action> = ['jam', 'dinger', 'deuce', 'slot'];

/** The various overtime methods. */
type OvertimeMethod = 'sudden death' | 'first to ten';

/** Which team are we talking about. */
type WhichTeam = 'home' | 'away' | 'both';

/** Defines the a gherkin parameter type called WhichTeam. */
defineParameterType({
    name: 'OvertimeMethod',
    regexp: RegExp('sudden death|first to ten'),
    transformer: (method: string): OvertimeMethod => {
        return method.toLowerCase().trim() as OvertimeMethod;
    },
});

/** Defines the a gherkin parameter type called WhichTeam. */
defineParameterType({
    name: 'WhichTeam',
    regexp: RegExp('home|away|both'),
    transformer: (team: string): WhichTeam => {
        return team.toLowerCase().replace(' ', '') as WhichTeam;
    },
});

/** Defines the a gherkin parameter type called Action. */
defineParameterType({
    name: 'Action',
    regexp: RegExp('jam|dinger|deuce|slot'),
    transformer: (action: string): Action => {
        return action.toLowerCase().replace(' ', '').trim() as Action;
    },
});

/** Defines the a gherkin parameter type called WhichTeam. */
defineParameterType({
    name: 'OnOrOff',
    regexp: RegExp('enabled|disabled'),
    transformer: (method: string): boolean => {
        return method.toLowerCase().trim() == 'enabled';
    },
});

/** Store all the game sheet submissions. */
const scoreappHook = (): void => {
    cy.intercept({
        url: 'save_sheet',
        method: 'POST',
    }).as('savedGamesheet');
};
beforeEach(scoreappHook);

/**
 * Save a match between two teams that takes place today.
 * @param homeTeam the home team
 * @param awayTeam  the away team
 * @param session  the session that match occurs in
 * @param field the field the match is played on
 * @return the wrapped match
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

/**
 * Help method for setting the score of a given team.
 * @param team_id the id of the team who score is being set
 * @param score the score of the team
 */
const setScore = (team_id: number, score: number): void => {
    let i = 0;
    while (i < score) {
        cy.window().its('scoreApp').invoke('addScore', team_id, 1);
        i += 1;
    }
};

/**
 * Set the scores of both team.
 * @param home_score the score of the home team
 * @param away_score  the score of the away team
 */
const setBothScores = (home_score: number, away_score: number): void => {
    cy.window().its('scoreApp').invoke('reset');
    cy.get<Match>('@match').then((match) => {
        expect(match.away_team_id).to.not.be.null;
        expect(match.home_team_id).to.not.be.null;
        if (match.home_team_id != null && match.away_team_id != null) {
            setScore(match.home_team_id, home_score);
            setScore(match.away_team_id, away_score);
        }
    });
};
Given(`home score is {int} and away score is {int}`, setBothScores);

/** Set the score for the given team. */
const setScoreStep = (team: WhichTeam, score: number): void => {
    // reset the game
    cy.window().its('scoreApp').invoke('reset');
    cy.get<Match>('@match').then((match) => {
        // get the match and set the score by adding 1 until get to the score
        if (team == 'home' && match.home_team_id != null) {
            setScore(match.home_team_id, score);
        } else if (team == 'away' && match.away_team_id != null) {
            setScore(match.away_team_id, score);
        } else if (team == 'both' && match.away_team_id != null && match.home_team_id != null) {
            setScore(match.away_team_id, score);
            setScore(match.home_team_id, score);
        } else {
            expect(match.home_team_id).to.be.not.null;
            expect(match.away_team_id).to.be.not.null;
        }
    });
};
When(`{WhichTeam} team(s) score are {int}`, setScoreStep);
When(`{WhichTeam} team(s) score is {int}`, setScoreStep);

/** Assert that both overtime options are enabled. */
const assertOvertimeOptions = (): void => {
    cy.findByRole('button', { name: RegExp('first to ten' as OvertimeMethod, 'i') })
        .should('be.visible')
        .should('be.enabled');
    cy.findByRole('button', { name: RegExp('sudden death', 'i') })
        .should('be.visible')
        .should('be.enabled');
};
Given(`overtime options are visible`, assertOvertimeOptions);

/** Simulate some action by a team. */
const commitAction = (team: WhichTeam, action: Action): void => {
    cy.findByRole('button', { name: RegExp(`${team}.*${action}`, 'i') }).click();
};
When(`{WhichTeam} team gets a {Action}`, commitAction);

/** Press the hammer regardless of where it is. */
const pressHammer = (): void => {
    cy.findByRole('button', { name: RegExp(`hammer`, 'i') }).click();
};
When(`the hammer is pressed`, pressHammer);

/** Select one of the overtime methods by clicking its button. */
const selectOvertime = (method: OvertimeMethod): void => {
    cy.findByRole('button', { name: RegExp(method, 'i') }).click();
};
When('{OvertimeMethod} overtime method is selected', selectOvertime);

/** Submit the gamesheet. */
const submitGamesheet = (): void => {
    cy.findByRole('button', { name: /submit score/i }).click();
};
Then(`the gamesheet is submitted`, submitGamesheet);

/** Assert the score of the team. */
const assertTeamScore = (team: WhichTeam, score: number): void => {
    if (team == 'home') {
        cy.get('[data-cy=homeScore]').contains(score);
    } else {
        cy.get('[data-cy=awayScore]').contains(score);
    }
};
Then(`{WhichTeam} team score becomes {int}`, assertTeamScore);

/** Assert able to submit the game sheet. */
const assertAbleToSubmit = (): void => {
    cy.findByRole('button', { name: /submit score/i })
        .should('be.visible')
        .should('be.enabled');
};
Then(`able to submit the gamesheet`, assertAbleToSubmit);

/**
 * A helper function for asserting state of team controls
 * @param team the away team or home team (not both)
 * @param currentState  whether the team controls should ne enabled or disabled
 */
const assertTeamControlHelper = (team: WhichTeam, currentState: boolean): void => {
    ACTIONS.forEach((action) => {
        cy.findByRole('button', { name: RegExp(`${team}.*${action}`, 'i') }).should('be.visible');
        if (currentState) {
            cy.findByRole('button', { name: RegExp(`${team}.*${action}`, 'i') }).should('be.enabled');
        } else {
            cy.findByRole('button', { name: RegExp(`${team}.*${action}`, 'i') }).should('be.disabled');
        }
    });
};

/**
 * A step to assert the team controls.
 * @param team which team controls to assert (home, away, both)
 * @param currentState whether the team controls should ne enabled or disabled
 */
const assertTeamControls = (team: WhichTeam, currentState: boolean): void => {
    if (team == 'both') {
        assertTeamControlHelper('away', currentState);
        assertTeamControlHelper('home', currentState);
    } else {
        assertTeamControlHelper(team, currentState);
    }
};
Then(`{WhichTeam} team controls are {OnOrOff}`, assertTeamControls);

/**
 * Assert which overtime method to used
 *
 * This is a bit over reliant on underlying details that I would want
 * @param method the method in overtime to use
 */
const assertOvertimeMethod = (method: OvertimeMethod): void => {
    if (method == 'first to ten') {
        // going to be a number greater than 0
        cy.window().its('scoreApp').invoke('whichOvertimeMethod').should('be.gt', 0);
    } else {
        const expectResult = method.replace(' ', '_');
        cy.window().its('scoreApp').invoke('whichOvertimeMethod').should('eq', expectResult);
    }
};
Then(`the app is using {OvertimeMethod} method`, assertOvertimeMethod);

/** Assert the which team has the hammer. */
const assertWhichTeamHasHammer = (team: WhichTeam): void => {
    cy.log(`${team}.*hammer`);
    cy.findByRole('button', { name: RegExp(`${team}.*hammer`, 'i') })
        .should('be.visible')
        .should('be.enabled');
};
Then(`{WhichTeam} team has the hammer`, assertWhichTeamHasHammer);

/** Assert that the gamesheet is saved. */
const assertGamesheetSaved = (): void => {
    cy.wait('@savedGamesheet').then((interception) => {
        expect(interception.response?.statusCode).to.be.eq(200);
        const sheet: Sheet = interception.response?.body as Sheet;
        cy.log(`Id of saved sheet: ${sheet.id}`);
        expect(sheet).to.haveOwnProperty('id');
        expect(sheet.id).to.not.be.null;
        // double check the right team won
        if (sheet.away_score > sheet.home_score) {
            cy.get('[data-cy=away_wins]').contains(1);
        } else {
            cy.get('[data-cy=home_wins]').contains(1);
        }
    });
};
Then(`gamesheet is saved`, assertGamesheetSaved);

/** Assert that app was reset for the next game. */
const assertAppReset = (): void => {
    cy.window().its('scoreApp').invoke('whichOvertimeMethod').should('be.null');
    assertTeamControls('home', true);
    assertTeamControls('away', true);
    assertTeamScore('home', 0);
    assertTeamScore('away', 0);
};
Then(`the app resets for next game`, assertAppReset);
