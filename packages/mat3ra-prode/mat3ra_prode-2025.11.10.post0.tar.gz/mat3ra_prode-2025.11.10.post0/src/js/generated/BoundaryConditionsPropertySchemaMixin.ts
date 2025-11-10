import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { BoundaryConditionsPropertySchema } from "@mat3ra/esse/dist/js/types";

export type BoundaryConditionsPropertySchemaMixin = Omit<
    BoundaryConditionsPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type BoundaryConditionsPropertyInMemoryEntity = InMemoryEntity &
    BoundaryConditionsPropertySchemaMixin;

export function boundaryConditionsPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & BoundaryConditionsPropertySchemaMixin = {
        get name() {
            return this.requiredProp<BoundaryConditionsPropertySchema["name"]>("name");
        },
        get type() {
            return this.requiredProp<BoundaryConditionsPropertySchema["type"]>("type");
        },
        get offset() {
            return this.requiredProp<BoundaryConditionsPropertySchema["offset"]>("offset");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
