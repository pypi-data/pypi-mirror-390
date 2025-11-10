import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { MagneticMomentsPropertySchema } from "@mat3ra/esse/dist/js/types";

export type MagneticMomentsPropertySchemaMixin = Omit<
    MagneticMomentsPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type MagneticMomentsPropertyInMemoryEntity = InMemoryEntity &
    MagneticMomentsPropertySchemaMixin;

export function magneticMomentsPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & MagneticMomentsPropertySchemaMixin = {
        get name() {
            return this.requiredProp<MagneticMomentsPropertySchema["name"]>("name");
        },
        get values() {
            return this.requiredProp<MagneticMomentsPropertySchema["values"]>("values");
        },
        get units() {
            return this.requiredProp<MagneticMomentsPropertySchema["units"]>("units");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
