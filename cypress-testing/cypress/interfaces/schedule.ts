/** The scheduled game interface. */
export interface ScheduledGame {
    home_team: string;
    home_team_id: number;
    away_team: string;
    away_team_id: number;
    field: string;
    field_id: number;
    date: string;
    time: string;
    datetime: string;
    session: string;
    session_id: number;
    id: number;
    status: string;
    result_link: string;
    home_team_link: string;
    away_team_link: string;
    field_link: string;
}
