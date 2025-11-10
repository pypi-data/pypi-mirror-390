import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { PropertyHolderSchema } from "@mat3ra/esse/dist/js/types";

export type PropertyHolderSchemaMixin = Omit<
    PropertyHolderSchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type PropertyHolderInMemoryEntity = InMemoryEntity & PropertyHolderSchemaMixin;

export function propertyHolderSchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & PropertyHolderSchemaMixin = {
        get group() {
            return this.prop<PropertyHolderSchema["group"]>("group");
        },
        get data() {
            return this.requiredProp<PropertyHolderSchema["data"]>("data");
        },
        get source() {
            return this.requiredProp<PropertyHolderSchema["source"]>("source");
        },
        get exabyteId() {
            return this.requiredProp<PropertyHolderSchema["exabyteId"]>("exabyteId");
        },
        get precision() {
            return this.prop<PropertyHolderSchema["precision"]>("precision");
        },
        get systemTags() {
            return this.prop<PropertyHolderSchema["systemTags"]>("systemTags");
        },
        get repetition() {
            return this.requiredProp<PropertyHolderSchema["repetition"]>("repetition");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
