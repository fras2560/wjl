import { Player } from '@Interfaces/player';
import { Field } from '@Interfaces/field';
/** An interface for a team. */
export interface Team {
    /** The id of the team. (Null when team does not exist yet). */
    id: number | null;
    /** The name of the team. */
    name: string;
    /** A list of players on the team. */
    players: Array<Player>;
    /** The home field of the team. */
    homefield: Field | null;
}
