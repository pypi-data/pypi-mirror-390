import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { DielectricTensorPropertySchema } from "@mat3ra/esse/dist/js/types";

export type DielectricTensorPropertySchemaMixin = Omit<
    DielectricTensorPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type DielectricTensorPropertyInMemoryEntity = InMemoryEntity &
    DielectricTensorPropertySchemaMixin;

export function dielectricTensorPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & DielectricTensorPropertySchemaMixin = {
        get name() {
            return this.requiredProp<DielectricTensorPropertySchema["name"]>("name");
        },
        get values() {
            return this.requiredProp<DielectricTensorPropertySchema["values"]>("values");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
