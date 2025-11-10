import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { SurfaceEnergyPropertySchema } from "@mat3ra/esse/dist/js/types";

export type SurfaceEnergyPropertySchemaMixin = Omit<
    SurfaceEnergyPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type SurfaceEnergyPropertyInMemoryEntity = InMemoryEntity & SurfaceEnergyPropertySchemaMixin;

export function surfaceEnergyPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & SurfaceEnergyPropertySchemaMixin = {
        get name() {
            return this.requiredProp<SurfaceEnergyPropertySchema["name"]>("name");
        },
        get units() {
            return this.requiredProp<SurfaceEnergyPropertySchema["units"]>("units");
        },
        get value() {
            return this.requiredProp<SurfaceEnergyPropertySchema["value"]>("value");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
