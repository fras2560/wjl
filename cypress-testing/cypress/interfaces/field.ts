/** The interface for the field. */
export interface Field {
    /** The name of the field. */
    name: string;
    /** The identifier of the field. */
    id: number | null;
    /** A google map link to the field. */
    link: string | null;
    /** A description about the field. */
    description: string | null;
}
