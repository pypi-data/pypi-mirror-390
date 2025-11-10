import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { IsRelaxedPropertySchema } from "@mat3ra/esse/dist/js/types";

export type IsRelaxedPropertySchemaMixin = Omit<
    IsRelaxedPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type IsRelaxedPropertyInMemoryEntity = InMemoryEntity & IsRelaxedPropertySchemaMixin;

export function isRelaxedPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & IsRelaxedPropertySchemaMixin = {
        get name() {
            return this.requiredProp<IsRelaxedPropertySchema["name"]>("name");
        },
        get value() {
            return this.requiredProp<IsRelaxedPropertySchema["value"]>("value");
        },
        get materialId() {
            return this.requiredProp<IsRelaxedPropertySchema["materialId"]>("materialId");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
