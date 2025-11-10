import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { ProtoPropertyHolderSchema } from "@mat3ra/esse/dist/js/types";

export type ProtoPropertyHolderSchemaMixin = Omit<
    ProtoPropertyHolderSchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type ProtoPropertyHolderInMemoryEntity = InMemoryEntity & ProtoPropertyHolderSchemaMixin;

export function protoPropertyHolderSchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & ProtoPropertyHolderSchemaMixin = {
        get data() {
            return this.requiredProp<ProtoPropertyHolderSchema["data"]>("data");
        },
        get source() {
            return this.requiredProp<ProtoPropertyHolderSchema["source"]>("source");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
