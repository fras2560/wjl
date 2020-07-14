/** The player interface. */
export interface Player {
    /** The email of the player. */
    email: string;
    /** The name of the player. */
    name: string;
    /** Whether the player has convenor access. */
    is_convenor: boolean;
    /** The id of the player. */
    id: number | null;
}
