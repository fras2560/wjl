import { Then } from 'cypress-cucumber-preprocessor/steps';
import { Field } from '@Interfaces/field';

/** Assert that details about some field are displayed. */
const assertDetailsAboutField = (): void => {
    cy.get<Field>('@field').then((field) => {
        cy.findByRole('document', { name: /field/i }).should('exist');
        cy.findByRole('img', { name: /google/i }).should('be.visible');
        cy.findByRole('heading', { name: RegExp(field.name, 'i') }).should('be.visible');
    });
};
Then(`see details about the field`, assertDetailsAboutField);
