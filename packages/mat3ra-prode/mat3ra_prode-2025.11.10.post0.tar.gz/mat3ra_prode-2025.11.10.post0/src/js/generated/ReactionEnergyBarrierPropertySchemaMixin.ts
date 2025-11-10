import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { ReactionEnergyBarrierPropertySchema } from "@mat3ra/esse/dist/js/types";

export type ReactionEnergyBarrierPropertySchemaMixin = Omit<
    ReactionEnergyBarrierPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type ReactionEnergyBarrierPropertyInMemoryEntity = InMemoryEntity &
    ReactionEnergyBarrierPropertySchemaMixin;

export function reactionEnergyBarrierPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & ReactionEnergyBarrierPropertySchemaMixin = {
        get name() {
            return this.requiredProp<ReactionEnergyBarrierPropertySchema["name"]>("name");
        },
        get units() {
            return this.requiredProp<ReactionEnergyBarrierPropertySchema["units"]>("units");
        },
        get value() {
            return this.requiredProp<ReactionEnergyBarrierPropertySchema["value"]>("value");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
