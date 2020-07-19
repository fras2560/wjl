/** The interface for a gamesheet in a match. */
export interface Sheet {
    /** The score of the home team. */
    home_score: number;
    /** Whether the home team hit a slot. */
    home_slot: boolean;
    /** How many jams (3-pointers) the home team has. */
    home_jams: number;
    /** How many dingers (1-pointers) the home team has. */
    home_dingers: number;
    /** How many deuces (2-pointers) the home team has */
    home_deuces: number;
    /** The score of the away team. */
    away_score: number;
    /** Whether the away team hit a slot. */
    away_slot: boolean;
    /** How many jams (3-pointers) the away team has. */
    away_jams: number;
    /** How many dingers (1-pointers) the away team has. */
    away_dingers: number;
    /** How many deuces (2-pointers) the away team has */
    away_deuces: number;
    /** The id of the sheet. */
    id: number | null;
    /** The id of the match the sheet is for. */
    match_id: number;
}
