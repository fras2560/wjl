/* eslint-disable @typescript-eslint/no-explicit-any */
import { Then, When } from 'cypress-cucumber-preprocessor/steps';
import { defineParameterType } from 'cypress-cucumber-preprocessor/steps';
import { SessionInterface } from '@Interfaces/session';
import { TeamRecord } from '@Interfaces/teamRecord';

/** The columns in the standings table. */
type StandingsColumn = 'jams' | 'wins' | 'losses' | 'jams' | 'slots';

/** Defines the a gherkin parameter type called StandingsColumn. */
defineParameterType({
    name: 'StandingsColumn',
    regexp: new RegExp('jams|team|wins|losses|points|jams|slots'),
    transformer: (column: string): StandingsColumn => {
        return column as StandingsColumn;
    },
});

/** Store all the standings tables data as it is requested. */
const standingsHook = (): void => {
    cy.request({
        url: 'api/session',
        method: 'GET',
    }).then((sessions) => {
        sessions.body.forEach((element: SessionInterface) => {
            cy.wrap(element).as(`session${element.id}`);
            cy.intercept('GET', `/standings/${element.id}`).as(`standings${element.id}`);
        });
    });
};
beforeEach(standingsHook);

/**
 * Calculate the win percentage of the given record.
 *
 * @param record the team records
 */
const calculateWinPercentage = (record: TeamRecord): number => {
    const winPercentage = record.wins / record.games_played;
    return isNaN(winPercentage) ? 0 : winPercentage;
};

/** Find which session is active. */
const getActiveSession = (): void => {
    cy.findAllByRole('tab').each((session) => {
        if (session.hasClass('active')) {
            const sessionId = session.attr('id')?.replace('Link', '');
            cy.get(`@${sessionId}`).as('active_session');
        }
    });
};

/** Assert teams are order by win percentage. */
const orderByWins = (): void => {
    getActiveSession();
    cy.get<SessionInterface>('@active_session').then((session) => {
        cy.wait(`@standings${session.id}`).then((interception) => {
            const standings = interception.response?.body as Array<TeamRecord>;
            let previousWins = 1.0;
            cy.findAllByRole('row').each((row, index) => {
                if (index > 0) {
                    const winPercentage = calculateWinPercentage(standings[index - 1]);
                    expect(row.text(), 'Expectining team name').to.contains(standings[index - 1].name);
                    expect(winPercentage).to.be.at.most(previousWins);
                    previousWins = winPercentage;
                }
            });
        });
    });
};
Then(`the teams are ordered by win percentage`, orderByWins);

/** Click the column header. */
const clickColumnHeading = (column: StandingsColumn): void => {
    // click the column header twice so decending order
    const click = ($el: JQuery<HTMLElement>): JQuery<HTMLElement> => {
        $el.trigger('click');
        return $el;
    };

    cy.findByRole('columnheader', { name: RegExp(column, 'i') })
        .pipe(click)
        .should('have.class', 'sorting_asc');
    cy.findByRole('columnheader', { name: RegExp(column, 'i') }).click();
};
When(`I sort by {StandingsColumn}`, clickColumnHeading);

/** Assert the table is sorted by the given column. */
const assertSortedByColumn = (column: StandingsColumn): void => {
    // click the column header
    getActiveSession();
    cy.get<SessionInterface>('@active_session').then((session) => {
        cy.wait(`@standings${session.id}`).then((interception) => {
            const standings = interception.response?.body as Array<TeamRecord>;
            // sort the data by the column
            standings.sort((a: TeamRecord, b: TeamRecord) => {
                // want to sort in descending order
                return a[column] > b[column] ? -1 : b[column] > a[column] ? 1 : 0;
            });
            // now assort that matches the same list
            cy.findAllByRole('row').each((row, index) => {
                if (index > 0) {
                    expect(row.text()).to.contains(standings[index - 1].name);
                }
            });
        });
    });
};
Then(`the teams are ordered by {StandingsColumn}`, assertSortedByColumn);

/** Search for some team. */
const searchForTeam = (): void => {
    getActiveSession();
    cy.get<SessionInterface>('@active_session').then((session) => {
        cy.wait(`@standings${session.id}`).then((interception) => {
            const standings = interception.response?.body as Array<TeamRecord>;
            const someTeam = standings[0];
            cy.findByRole('searchbox', { name: /search/i }).type(someTeam.name);
            cy.wrap(someTeam).as('search_team');
            cy.wrap(standings).as('standings');
        });
    });
};
When(`I search for a team`, searchForTeam);

/** Assert the team that was search is visible. */
const assertSearchTeamVisisble = (): void => {
    cy.get<TeamRecord>('@search_team').then((team) => {
        cy.findByRole('row', { name: RegExp(team.name, 'i') }).should('be.visible');
    });
};
Then(`the team is visible`, assertSearchTeamVisisble);

/** Click on some team. */
const clickOnTeam = (): void => {
    getActiveSession();
    cy.get<SessionInterface>('@active_session').then((session) => {
        cy.wait(`@standings${session.id}`).then((interception) => {
            const standings = interception.response?.body as Array<TeamRecord>;
            const someTeam = standings[0];
            cy.findByRole('link', { name: RegExp(someTeam.name, 'i') }).click();
            cy.wrap(someTeam.name).as('team');
        });
    });
};
When(`click on a team link`, clickOnTeam);

/** Assert that no team is visible other than team that was searcheed. */
const assertNoOtherTeamVisisble = (): void => {
    cy.get<Array<TeamRecord>>(`@standings`).then((standings) => {
        cy.get<TeamRecord>('@search_team').then((searchTeam) => {
            standings.forEach((team: TeamRecord) => {
                if (team.name != searchTeam.name) {
                    cy.findByRole('row', { name: RegExp(team.name, 'i') }).should('not.exist');
                }
            });
        });
    });
};
Then(`no other team is visible`, assertNoOtherTeamVisisble);
