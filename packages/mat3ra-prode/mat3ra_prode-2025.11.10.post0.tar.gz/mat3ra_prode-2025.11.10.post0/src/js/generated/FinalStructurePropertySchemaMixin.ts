import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { FinalStructurePropertySchema } from "@mat3ra/esse/dist/js/types";

export type FinalStructurePropertySchemaMixin = Omit<
    FinalStructurePropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type FinalStructurePropertyInMemoryEntity = InMemoryEntity &
    FinalStructurePropertySchemaMixin;

export function finalStructurePropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & FinalStructurePropertySchemaMixin = {
        get name() {
            return this.requiredProp<FinalStructurePropertySchema["name"]>("name");
        },
        get isRelaxed() {
            return this.requiredProp<FinalStructurePropertySchema["isRelaxed"]>("isRelaxed");
        },
        get materialId() {
            return this.requiredProp<FinalStructurePropertySchema["materialId"]>("materialId");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
