import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { AtomicForcesPropertySchema } from "@mat3ra/esse/dist/js/types";

export type AtomicForcesPropertySchemaMixin = Omit<
    AtomicForcesPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type AtomicForcesPropertyInMemoryEntity = InMemoryEntity & AtomicForcesPropertySchemaMixin;

export function atomicForcesPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & AtomicForcesPropertySchemaMixin = {
        get name() {
            return this.requiredProp<AtomicForcesPropertySchema["name"]>("name");
        },
        get values() {
            return this.requiredProp<AtomicForcesPropertySchema["values"]>("values");
        },
        get units() {
            return this.requiredProp<AtomicForcesPropertySchema["units"]>("units");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
