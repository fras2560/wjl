/**
 * A model for a player in the league
 */
export class Player {
    /** The email of the player. */
    email: string;
    /** The name of the player. */
    name: string;
    /** Whether the player is a convenor or not. */
    is_convenor: boolean;

    /**
     * Constructrs a player object.
     * @param email the email of the player
     * @param name the name of the player
     * @param is_convenor whether they are a convenor or not (default=False)
     */
    constructor(email: string, name: string, is_convenor = false) {
        this.email = email;
        this.name = name;
        this.is_convenor = is_convenor;
    }
}