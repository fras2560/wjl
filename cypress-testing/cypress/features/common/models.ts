/* eslint-disable @typescript-eslint/camelcase */
import { Given } from 'cypress-cucumber-preprocessor/steps';
import { randomName, randomEmail } from './login';
import { SessionInterface } from '@Interfaces/session';
/** A constant link to use when creating new field */
const FIELD_LINK = `https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d1447.8584120111693!2d-80.53118577391533!3d43.4665087914418!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x882bf405af73801f%3A0x27310fca90b0ddb!2sWaterloo%20Park!5e0!3m2!1sen!2sca!4v1594648738206!5m2!1sen!2sca`;

/** Create some league sesssion. */
const createLeagueSession = (): void => {
    cy.login({ email: randomEmail(), name: randomName(), is_convenor: true });
    const sesh: SessionInterface = { name: randomName(), id: null };
    cy.request({
        url: 'api/session/save',
        method: 'POST',
        body: sesh,
    });
    cy.wrap(sesh).as('current_session');
    cy.logout();
};
Given(`there is a league session`, createLeagueSession);

/** Create some field. */
const createField = (): void => {
    const fieldName = `Field ${randomName()}`;
    cy.login({ email: randomEmail(), name: randomName(), is_convenor: true });
    const field = { id: null, name: fieldName, description: `Testing field`, link: FIELD_LINK };
    cy.request({
        url: 'api/field/save',
        method: 'POST',
        body: field,
    }).then((xhr) => {
        const field = xhr.body;
        expect(field).to.have.property('name', fieldName);
        cy.wrap(field).as('field');
    });
    cy.logout();
};
Given(`a field exists`, createField);
