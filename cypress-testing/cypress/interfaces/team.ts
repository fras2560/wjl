import { Player } from '@Interfaces/player';
import { Field } from '@Interfaces/field';
export interface Team {
    id: number | null;
    name: string;
    players: Array<Player>;
    homefield: Field;
}
