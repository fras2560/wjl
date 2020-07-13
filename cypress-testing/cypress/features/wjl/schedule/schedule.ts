import { Then, When } from 'cypress-cucumber-preprocessor/steps';
import { SessionInterface } from '@Interfaces/session';
import { Field } from '@Interfaces/field';
import { ScheduledGame } from '@Interfaces/schedule';

/** Store all the schedules tables data as it is requested. */
const schedulesHook = (): void => {
    cy.server();
    cy.request({
        url: 'api/session',
        method: 'GET',
    }).then((sessions) => {
        sessions.body.forEach((element: SessionInterface) => {
            cy.wrap(element).as(`session${element.id}`);
            cy.route('GET', `/schedule/${element.id}`).as(`schedule${element.id}`);
        });
    });
};
beforeEach(schedulesHook);

/** Find which session is active. */
const getActiveSession = (): void => {
    cy.findAllByRole('tab').each((session) => {
        if (session.hasClass('active')) {
            const sessionId = session.attr('id')?.replace('Link', '');
            cy.get(`@${sessionId}`).as('active_session');
        }
    });
};

/** Click on some team. */
const clickOnTeam = (): void => {
    getActiveSession();
    cy.get<string>('@search_team').then((team) => {
        cy.findAllByRole('link', { name: RegExp(team, 'i') })
            .eq(1)
            .click();
        cy.wrap(team).as('team');
    });
};
When(`click on a team link`, clickOnTeam);

/** Click on field link. */
const clickOnField = (): void => {
    getActiveSession();
    cy.get<Field>('@search_field').then((field) => {
        cy.findAllByRole('link', { name: RegExp(field.name, 'i') })
            .eq(1)
            .click();
        cy.wrap(field).as('field');
    });
};
When(`click on a field link`, clickOnField);

/** Search for some team. */
const searchForTeam = (): void => {
    getActiveSession();
    cy.get<SessionInterface>('@active_session').then((session) => {
        cy.wait(`@schedule${session.id}`).then((xhr) => {
            const schedule = xhr.responseBody as Array<ScheduledGame>;
            const someTeam = schedule[0].home_team;
            cy.findByRole('searchbox', { name: /search/i }).type(someTeam);
            cy.wrap(someTeam).as('search_team');
            cy.wrap(schedule).as('schedule');
        });
    });
};
When(`I search for a team`, searchForTeam);

/** Search for some field. */
const searchForField = (): void => {
    getActiveSession();
    cy.get<SessionInterface>('@active_session').then((session) => {
        cy.wait(`@schedule${session.id}`).then((xhr) => {
            const schedule = xhr.responseBody as Array<ScheduledGame>;
            const someField = schedule[1].field;
            cy.findByRole('searchbox', { name: /search/i }).type(someField);
            const fieldInterface: Field = { id: schedule[1].field_id, name: someField, description: null, link: null };
            cy.wrap(fieldInterface).as('search_field');
            cy.wrap(schedule).as('schedule');
        });
    });
};
When(`I search for a field`, searchForField);

/** Assert schedule is displayed. */
const assertScheduleDisplayed = (): void => {
    getActiveSession();
    cy.get<SessionInterface>('@active_session').then((session) => {
        cy.wait(`@schedule${session.id}`).then((xhr) => {
            const schedule = xhr.responseBody as Array<ScheduledGame>;
            cy.get('#session_table_1_info').then((element) => {
                // need to find the starting index
                // since the schedule page jumps to current date
                const match = element.text().match(/\d+/);
                const startingIndex = match != null ? Number.parseInt(match[0]) - 1 : 0;
                cy.log(`${startingIndex}`);
                cy.findAllByRole('row').each((row, index) => {
                    if (index > 0) {
                        expect(row.text()).to.contains(schedule[startingIndex + index - 1].home_team);
                        expect(row.text()).to.contains(schedule[startingIndex + index - 1].away_team);
                        expect(row.text()).to.contains(schedule[startingIndex + index - 1].date);
                    }
                });
            });
        });
    });
};
Then(`the schedule is displayed`, assertScheduleDisplayed);

/** Assert the team that was search is visible. */
const assertTeamsGames = (): void => {
    cy.get<string>('@search_team').then((team) => {
        // make sure the games are visible
        cy.findAllByRole('row', { name: RegExp(team, 'i') }).should('be.visible');
        // ensure all their games are displayed
        cy.get('#session_table_1_info').then((element) => {
            // get the number of total games from the info
            const matches = element.text().match(/of \d+/);
            const totalMatches = matches != null ? Number.parseInt(matches[0].replace('of', '').trim()) : 0;
            cy.get<Array<ScheduledGame>>('@schedule').then((schedule) => {
                const teamGames = schedule.filter(
                    (game: ScheduledGame) => game.home_team == team || game.away_team == team,
                );
                expect(teamGames.length).to.eq(totalMatches);
            });
        });
    });
};
Then(`can see all the team's games`, assertTeamsGames);
