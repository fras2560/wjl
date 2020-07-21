/** An interface for requesting to join or leave a team. */
export interface TeamRequest {
    /** The id of the team that request is being made for. */
    team_id: number;
    /** The id of the player making the request is being. */
    player_id: number;
    /** Whether the player is registering or leaving the team. */
    register: boolean;
}
