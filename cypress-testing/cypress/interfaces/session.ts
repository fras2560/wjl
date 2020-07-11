/** A league session. */

/** The league session interface for responses from API. */
export interface SessionInterface {
    name: string;
    id: number;
}

/** The simple league session model. */
export class Session {
    /** The name of the legaue session. */
    name: string;

    /** Constructs a league session. */
    constructor(name: string) {
        this.name = name;
    }
}
