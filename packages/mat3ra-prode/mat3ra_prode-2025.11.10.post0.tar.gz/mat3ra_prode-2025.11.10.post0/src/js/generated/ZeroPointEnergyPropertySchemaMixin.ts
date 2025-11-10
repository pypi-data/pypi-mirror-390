import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { ZeroPointEnergyPropertySchema } from "@mat3ra/esse/dist/js/types";

export type ZeroPointEnergyPropertySchemaMixin = Omit<
    ZeroPointEnergyPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type ZeroPointEnergyPropertyInMemoryEntity = InMemoryEntity &
    ZeroPointEnergyPropertySchemaMixin;

export function zeroPointEnergyPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & ZeroPointEnergyPropertySchemaMixin = {
        get name() {
            return this.requiredProp<ZeroPointEnergyPropertySchema["name"]>("name");
        },
        get units() {
            return this.requiredProp<ZeroPointEnergyPropertySchema["units"]>("units");
        },
        get value() {
            return this.requiredProp<ZeroPointEnergyPropertySchema["value"]>("value");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
