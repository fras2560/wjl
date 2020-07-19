import { When } from 'cypress-cucumber-preprocessor/steps';
import { Field } from '@Interfaces/field';

/** Try to access the field by using a direct link. */
const accessField = (): void => {
    cy.get<Field>('@field').then((field) => {
        cy.visit(`field/${field.id}`);
    });
};
When(`I try to access the field`, accessField);
