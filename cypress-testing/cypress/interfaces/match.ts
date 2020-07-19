/** The interface for a match between two teams. */
export interface Match {
    /** The name of the home team. */
    home_team: string | null;
    /** The id of the home team. */
    home_team_id: number | null;
    /** The name of the away team. */
    away_team: string | null;
    /** The id of the away team. */
    away_team_id: number | null;
    /** The name of the field where match is happening. */
    field: string | null;
    /** The id of the field where match is happening. */
    field_id: number | null;
    /** The date of the match. (Format: YYYY-MM-DD) */
    date: string | null;
    /** The time of the match.  (Format: HH:MM)*/
    time: string | null;
    /** Both the date and time of the match (Format: YYYY-MM-DD HH:MM ) */
    datetime: string | null;
    /** The name of the session the match is part of. */
    session: string | null;
    /** The id of the session the match is part of. */
    session_id: number | null;
    /** The id of the match. */
    id: number | null;
    /** The status of the match. */
    status: string | null;
}
