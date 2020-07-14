/** The interface for a team record. */
export interface TeamRecord {
    /** The id of the team */
    id: number;
    /** The name of the team. */
    name: string;
    /** How many wins the team has. */
    wins: number;
    /** How many losses the team has. */
    losses: number;
    /** How many games the team has. */
    games_played: number;
    /** How many points the team has scored. */
    points_scored: number;
    /** How many jams the team has scored. */
    jams: number;
    /** How many slots the team has scored. */
    slots: number;
    /** A link to team's page. */
    team_link: string;
}
