import { Given } from 'cypress-cucumber-preprocessor/steps';
import { randomName, randomEmail } from './login';
import { Session } from '@Models/session';
import { Player } from '@Models/player';

const createLeagueSession = (): void => {
    cy.login(new Player(randomEmail(), randomName(), true));
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
