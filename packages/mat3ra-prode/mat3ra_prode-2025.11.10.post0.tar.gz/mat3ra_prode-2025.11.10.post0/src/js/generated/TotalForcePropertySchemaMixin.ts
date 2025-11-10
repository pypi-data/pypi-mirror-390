import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { TotalForcesPropertySchema } from "@mat3ra/esse/dist/js/types";

export type TotalForcePropertySchemaMixin = Omit<
    TotalForcesPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type TotalForcePropertyInMemoryEntity = InMemoryEntity & TotalForcePropertySchemaMixin;

export function totalForcePropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & TotalForcePropertySchemaMixin = {
        get name() {
            return this.requiredProp<TotalForcesPropertySchema["name"]>("name");
        },
        get units() {
            return this.requiredProp<TotalForcesPropertySchema["units"]>("units");
        },
        get value() {
            return this.requiredProp<TotalForcesPropertySchema["value"]>("value");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
