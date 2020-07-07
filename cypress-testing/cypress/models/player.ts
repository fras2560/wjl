/**
 * A model for a player in the league
 */
export class Player {
    /** The email of the player. */
    email: string;
    /** The name of the player. */
    name: string;
    /** Whether the player is a convenor or not. */
    isConvenor: boolean;

    /**
     * Constructrs a player object.
     * @param email the email of the player
     * @param name the name of the player
     * @param isConvenor whether they are a convenor or not (default=False)
     */
    constructor(email: string, name: string, isConvenor = false) {
        this.email = email;
        this.name = name;
        this.isConvenor = isConvenor;
    }
}
