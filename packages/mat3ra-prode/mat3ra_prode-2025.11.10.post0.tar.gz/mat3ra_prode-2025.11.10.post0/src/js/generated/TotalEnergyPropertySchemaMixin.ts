import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { TotalEnergyPropertySchema } from "@mat3ra/esse/dist/js/types";

export type TotalEnergyPropertySchemaMixin = Omit<
    TotalEnergyPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type TotalEnergyPropertyInMemoryEntity = InMemoryEntity & TotalEnergyPropertySchemaMixin;

export function totalEnergyPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & TotalEnergyPropertySchemaMixin = {
        get name() {
            return this.requiredProp<TotalEnergyPropertySchema["name"]>("name");
        },
        get units() {
            return this.requiredProp<TotalEnergyPropertySchema["units"]>("units");
        },
        get value() {
            return this.requiredProp<TotalEnergyPropertySchema["value"]>("value");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
