import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { PotentialProfilePropertySchema } from "@mat3ra/esse/dist/js/types";

export type PotentialProfilePropertySchemaMixin = Omit<
    PotentialProfilePropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type PotentialProfilePropertyInMemoryEntity = InMemoryEntity &
    PotentialProfilePropertySchemaMixin;

export function potentialProfilePropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & PotentialProfilePropertySchemaMixin = {
        get xAxis() {
            return this.requiredProp<PotentialProfilePropertySchema["xAxis"]>("xAxis");
        },
        get yAxis() {
            return this.requiredProp<PotentialProfilePropertySchema["yAxis"]>("yAxis");
        },
        get name() {
            return this.requiredProp<PotentialProfilePropertySchema["name"]>("name");
        },
        get xDataArray() {
            return this.requiredProp<PotentialProfilePropertySchema["xDataArray"]>("xDataArray");
        },
        get yDataSeries() {
            return this.requiredProp<PotentialProfilePropertySchema["yDataSeries"]>("yDataSeries");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
