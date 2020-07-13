import { Then, When } from 'cypress-cucumber-preprocessor/steps';
import { Field } from '@Interfaces/field';

/** Try to access the field by using a direct link. */
const accessField = (): void => {
    cy.get<Field>('@field').then((field) => {
        cy.visit(`field/${field.id}`);
    });
};
When(`I try to access the field`, accessField);

/** Assert that details about some field are displayed. */
const assertDetailsAboutField = (): void => {
    cy.get<Field>('@field').then((field) => {
        cy.findByRole('document', { name: /field/i }).should('exist');
        cy.findByRole('img', { name: /google/i }).should('be.visible');
        cy.findByRole('heading', { name: RegExp(field.name, 'i') }).should('be.visible');
    });
};
Then(`see details about the field`, assertDetailsAboutField);
