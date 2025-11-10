import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { AtomicConstraintsPropertySchema } from "@mat3ra/esse/dist/js/types";

export type AtomicConstraintsPropertySchemaMixin = Omit<
    AtomicConstraintsPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type AtomicConstraintsPropertyInMemoryEntity = InMemoryEntity &
    AtomicConstraintsPropertySchemaMixin;

export function atomicConstraintsPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & AtomicConstraintsPropertySchemaMixin = {
        get name() {
            return this.requiredProp<AtomicConstraintsPropertySchema["name"]>("name");
        },
        get values() {
            return this.requiredProp<AtomicConstraintsPropertySchema["values"]>("values");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
