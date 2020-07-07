import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps';
import { defineParameterType } from 'cypress-cucumber-preprocessor/steps';

/** The team place in the standings. */
type TeamPlace = "first" | "last";

/**
 * Mocks the session standings
 * @param teamPosition the position of the user team
 * @param myTeamName the name of the team (My team)
 */
const mockTeams = (teamPosition: TeamPlace, myTeamName = "My Team" as string): void => {
    cy.fixture("standings.json").then((standings) => {
        // change the team name to my team name
        if (teamPosition == "first") {
            standings[0].name =myTeamName; 
        } else {
            standings[standings.length - 1].name =myTeamName;
        }
    });
}
Given(`my team is {TeamPlace} in the place`, mockTeams)


/** Navigate to the standings page. */
const navigateToStandings = (): void => {
    cy.visit("standings");
}
When(`I navigate to the standings page`, navigateToStandings);

/** Defines the a gherkin parameter type called Role. */
defineParameterType({
    name: "TeamPlace",
    regexp: new RegExp("first|last"),
    transformer: (place: string): TeamPlace => {
        return place as TeamPlace;
    },
});