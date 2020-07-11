/** The interface for a team record. */
export interface TeamRecord {
    id: number;
    name: string;
    wins: number;
    losses: number;
    games_played: number;
    points_scored: number;
    jams: number;
    slots: number;
    team_link: string;
}
