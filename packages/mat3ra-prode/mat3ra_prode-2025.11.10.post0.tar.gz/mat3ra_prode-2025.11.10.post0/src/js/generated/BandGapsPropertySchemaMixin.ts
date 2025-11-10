import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { BandGapsPropertySchema } from "@mat3ra/esse/dist/js/types";

export type BandGapsPropertySchemaMixin = Omit<
    BandGapsPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type BandGapsPropertyInMemoryEntity = InMemoryEntity & BandGapsPropertySchemaMixin;

export function bandGapsPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & BandGapsPropertySchemaMixin = {
        get name() {
            return this.requiredProp<BandGapsPropertySchema["name"]>("name");
        },
        get values() {
            return this.requiredProp<BandGapsPropertySchema["values"]>("values");
        },
        get eigenvalues() {
            return this.prop<BandGapsPropertySchema["eigenvalues"]>("eigenvalues");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
