import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { FermiEnergyPropertySchema } from "@mat3ra/esse/dist/js/types";

export type FermiEnergyPropertySchemaMixin = Omit<
    FermiEnergyPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type FermiEnergyPropertyInMemoryEntity = InMemoryEntity & FermiEnergyPropertySchemaMixin;

export function fermiEnergyPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & FermiEnergyPropertySchemaMixin = {
        get name() {
            return this.requiredProp<FermiEnergyPropertySchema["name"]>("name");
        },
        get units() {
            return this.requiredProp<FermiEnergyPropertySchema["units"]>("units");
        },
        get value() {
            return this.requiredProp<FermiEnergyPropertySchema["value"]>("value");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
