import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { PressurePropertySchema } from "@mat3ra/esse/dist/js/types";

export type PressurePropertySchemaMixin = Omit<
    PressurePropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type PressurePropertyInMemoryEntity = InMemoryEntity & PressurePropertySchemaMixin;

export function pressurePropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & PressurePropertySchemaMixin = {
        get name() {
            return this.requiredProp<PressurePropertySchema["name"]>("name");
        },
        get units() {
            return this.requiredProp<PressurePropertySchema["units"]>("units");
        },
        get value() {
            return this.requiredProp<PressurePropertySchema["value"]>("value");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
