/* eslint-disable @typescript-eslint/camelcase */
import uuidv4 from 'uuid/v4';
import { Player } from '@Interfaces/player';

/**
 * Creates a random name to use for testing.
 * @return a random name
 * @example
 * ```typescript
 * const firstName = randomName();
 * ```
 */
export function randomName(): string {
    return uuidv4().split('-')[0];
}

/**
 * Creates a random email to use for testing.
 * @return a random email with domain of @digitalEducationTesting
 * @example
 * ```typescript
 * const email = randomEmail();
 * ```
 */
export function randomEmail(): string {
    return randomName() + '-' + randomName() + '@wjl.ca';
}

/**
 * Returns some player;
 * @return some player
 */
export function somePlayer(): Player {
    return { email: randomEmail(), name: randomName(), is_convenor: false, id: null } as Player;
}
