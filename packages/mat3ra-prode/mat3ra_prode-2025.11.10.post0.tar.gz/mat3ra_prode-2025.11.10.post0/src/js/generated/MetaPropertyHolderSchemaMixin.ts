import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { MetaPropertyHolderSchema } from "@mat3ra/esse/dist/js/types";

export type MetaPropertyHolderSchemaMixin = Omit<
    MetaPropertyHolderSchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type MetaPropertyHolderInMemoryEntity = InMemoryEntity & MetaPropertyHolderSchemaMixin;

export function metaPropertyHolderSchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & MetaPropertyHolderSchemaMixin = {
        get data() {
            return this.requiredProp<MetaPropertyHolderSchema["data"]>("data");
        },
        get source() {
            return this.requiredProp<MetaPropertyHolderSchema["source"]>("source");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
