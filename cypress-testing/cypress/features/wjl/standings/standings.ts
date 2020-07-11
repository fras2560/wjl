import { Before, Given, Then } from 'cypress-cucumber-preprocessor/steps';
import { defineParameterType } from 'cypress-cucumber-preprocessor/steps';
import { SessionInterface } from '@Interfaces/session';
import { TeamRecord } from '@Interfaces/teamRecord';

/** Defines the a gherkin parameter type called Role. */
defineParameterType({
    name: 'TeamPlace',
    regexp: new RegExp('first|last'),
    transformer: (place: string): TeamPlace => {
        return place as TeamPlace;
    },
});

/** The team place in the standings. */
type TeamPlace = 'first' | 'last';

/** Store all the standings tables data as it is requested. */
const standingsHook = (): void => {
    cy.server();
    cy.request({
        url: 'api/session',
        method: 'GET',
    }).then((sessions) => {
        cy.log('Got all sessions');
        cy.log(sessions.body);
        sessions.body.forEach((element: SessionInterface) => {
            cy.wrap(element).as(`session${element.id}`);
            cy.route('GET', `/standings/${element.id}`).as(`standings${element.id}`);
        });
    });
};
before(standingsHook);

/** Assert teams are order by win percentage. */
const orderByWins = (): void => {
    cy.wait('@standings1').then((xhr) => {
        const standings = xhr.responseBody as Array<TeamRecord>;
        let previousWins = 1.0;
        cy.findAllByRole('row').each((row, index) => {
            if (index > 0) {
                const winPercentage = standings[index - 1].wins / standings[index - 1].games_played;
                expect(row.text()).to.contains(standings[index - 1].name);
                expect(winPercentage).to.be.at.most(previousWins);
                previousWins = winPercentage;
            }
        });
    });
};
Then(`the teams are ordered by win percentage`, orderByWins);
