/* eslint-disable @typescript-eslint/camelcase */
import { Given } from 'cypress-cucumber-preprocessor/steps';
import { randomName, randomEmail } from './login';
import { Session } from '@Interfaces/session';

const createLeagueSession = (): void => {
    cy.login({ email: randomEmail(), name: randomName(), is_convenor: true });
    const sesh = new Session(randomName());
    cy.request({
        url: 'api/session/save',
        method: 'POST',
        body: sesh,
    });
    cy.wrap(sesh).as('current_session');
    cy.logout();
};
Given(`there is a league session`, createLeagueSession);
