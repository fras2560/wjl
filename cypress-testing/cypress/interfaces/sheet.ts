/** The interface for a gamesheet in a match. */
export interface Sheet {
    home_score: number;
    home_slot: boolean;
    home_jams: number;
    home_dingers: number;
    home_deuces: number;
    away_score: number;
    away_slot: boolean;
    away_jams: number;
    away_dingers: number;
    away_deuces: number;
    id: number | null;
    match_id: number;
}
