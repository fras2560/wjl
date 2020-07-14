/** The scheduled game interface. */
export interface ScheduledGame {
    /** The name of the home team. */
    home_team: string;
    /** The id of the home team. */
    home_team_id: number;
    /** The name of the away team. */
    away_team: string;
    /** The id of the away team. */
    away_team_id: number;
    /** The name of the field. */
    field: string;
    /** The id of the field. */
    field_id: number;
    /** The date of the match. (Format: YYYY-MM-DD) */
    date: string;
    /** The time of the match.  (Format: HH:MM)*/
    time: string;
    /** Both the date and time of the match (Format: YYYY-MM-DD HH:MM ) */
    datetime: string;
    /** The name of the session the match is part of. */
    session: string;
    /** The id of the session the match is part of. */
    session_id: number;
    /** The id of the match */
    id: number;
    /** The status of the match. */
    status: string;
    /** A link to the results of the match. */
    result_link: string;
    /** A link to the home team's page */
    home_team_link: string;
    /** A link to the away team's page */
    away_team_link: string;
    /** A link to the field information. */
    field_link: string;
}
