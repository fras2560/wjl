/** The interface for a match between two teams. */
export interface Match {
    home_team: string | null;
    home_team_id: number | null;
    away_team: string | null;
    away_team_id: number | null;
    field: string | null;
    field_id: number | null;
    date: string | null;
    time: string | null;
    datetime: string | null;
    session: string | null;
    session_id: number | null;
    id: number | null;
    status: string | null;
}
