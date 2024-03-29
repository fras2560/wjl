import { Given, Then } from 'cypress-cucumber-preprocessor/steps';
import { randomName, randomEmail } from '@Common/helpers';
import { SessionInterface } from '@Interfaces/session';
import { Field } from '@Interfaces/field';
import { Player } from '@Interfaces/player';
import { Team } from '@Interfaces/team';
import { TeamRequest } from '@Interfaces/teamRequest';
/** A constant link to use when creating new field */
const FIELD_LINK = `https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d1447.8584120111693!2d-80.53118577391533!3d43.4665087914418!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x882bf405af73801f%3A0x27310fca90b0ddb!2sWaterloo%20Park!5e0!3m2!1sen!2sca!4v1594648738206!5m2!1sen!2sca`;

/** Create a session. */
export const createSession = (): Cypress.Chainable<SessionInterface> => {
    const name = randomName();
    const sesh: SessionInterface = { name: name, id: null };
    cy.request({
        url: 'api/session/save',
        method: 'POST',
        body: sesh,
    }).then((xhr) => {
        const session = xhr.body;
        expect(session).to.have.property('name', name);
        cy.wrap(session).as('current_session');
    });
    return cy.get<SessionInterface>('@current_session');
};

/** A step for creating a league session. */
const createSessionStep = (): void => {
    cy.login({ email: randomEmail(), name: randomName(), is_convenor: true, id: null });
    createSession();
    cy.logout();
};
Given(`there is a league session`, createSessionStep);

/** A function that creates a field. */
export const createField = (): Cypress.Chainable<Field> => {
    const fieldName = `Field ${randomName()}`;
    const field: Field = { id: null, name: fieldName, description: `Testing field`, link: FIELD_LINK };
    cy.request({
        url: 'api/field/save',
        method: 'POST',
        body: field,
    }).then((xhr) => {
        const field = xhr.body;
        expect(field).to.have.property('name', fieldName);
        cy.wrap(field).as('field');
    });
    return cy.get<Field>('@field');
};

/** A step that creates a field. */
const createFieldStep = (): void => {
    cy.login({ email: randomEmail(), name: randomName(), is_convenor: true, id: null });
    createField();
    cy.logout();
};
Given(`a field exists`, createFieldStep);

/**
 * Creates a team
 * @param players the list of players on the team
 * @param field the field of the team or null
 */
export const createTeam = (players: Array<Player>, field: Field | null): Cypress.Chainable<Team> => {
    const teamName = `Team ${randomName()}`;
    const team: Team = { id: null, name: teamName, homefield: field, players: players };
    cy.request({
        url: 'api/team/save',
        method: 'POST',
        body: team,
    }).then((xhr) => {
        const team = xhr.body;
        expect(team).to.have.property('name', teamName);
        cy.wrap(team).as('team');
    });
    return cy.get<Team>('@team');
};

/**
 * Updates a team.
 * @param team: the team to update
 */
export const updateTeam = (team: Team): Cypress.Chainable<Team> => {
    cy.request({
        url: 'api/team/save',
        method: 'PUT',
        body: team,
    }).then((xhr) => {
        const team = xhr.body;
        expect(team).to.have.property('name', team.name);
        cy.wrap(team).as('team');
    });
    return cy.get<Team>('@team');
};

/**
 * Register or de-register a player for given team.
 * @param player the player for who is registering/leaving
 * @param team the team the request is for
 * @param joining true if joining, false if leaving the team
 */
export const registerPlayerForTeam = (player: Player, team: Team, joining: boolean): void => {
    const teamRequest = { team_id: team.id, player_id: player.id, register: joining } as TeamRequest;
    cy.request({
        url: `api/team/registration`,
        method: 'POST',
        body: teamRequest,
    }).then((xhr) => {
        expect(xhr.status).to.be.eq(200);
        const team: Team = xhr.body as Team;
        if (joining) {
            expect(team.players).to.deep.include(player);
        } else {
            expect(team.players).to.not.deep.include(player);
        }
    });
};

/** Create some team. */
const createTeamStep = (): void => {
    cy.login({ email: randomEmail(), name: randomName(), is_convenor: true, id: null });
    createField();
    cy.get<Field>('@field').then((field) => {
        cy.get<Player>('@player').then((player) => {
            createTeam([player], field);
        });
    });
    cy.logout();
};
Given(`a team exists`, createTeamStep);

/** Assert that details about some field are displayed. */
const assertDetailsAboutField = (): void => {
    cy.get<Field>('@field').then((field) => {
        cy.findByRole('document', { name: /field/i }).should('exist');
        cy.findByRole('img', { name: /google/i }).should('be.visible');
        cy.findByRole('heading', { name: RegExp(field.name, 'i') }).should('be.visible');
    });
};
Then(`see details about the field`, assertDetailsAboutField);

/** Assert that details about some team are displayed. */
const assertDetailsAboutTeam = (): void => {
    cy.get<Team>('@team').then((team) => {
        const fieldName = team.homefield != null ? team.homefield.name : 'no homefield';
        cy.findByRole('document', { name: /team/i }).should('exist');
        cy.findByRole('heading', { name: RegExp(team.name, 'i') }).should('be.visible');
        cy.findByRole('heading', { name: RegExp(fieldName, 'i') }).should('be.visible');
        cy.findByRole('list', { name: /player/i }).should('be.visible');
        cy.findByRole('list', { name: /player/i }).within(() => {
            team.players.forEach((player: Player) => {
                cy.findByRole('listitem', { name: RegExp(player.name, 'i') }).should('be.visible');
            });
        });
    });
};
Then(`see details about the team`, assertDetailsAboutTeam);

/** Assert that on a team page for some team. */
const assertTeamPage = (): void => {
    cy.get<string>('@team').then((team) => {
        cy.findByRole('heading', { name: RegExp(team, 'i') }).should('be.visible');
    });
};
Then(`I see more information about the team`, assertTeamPage);
