import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { ReactionEnergyProfilePropertySchema } from "@mat3ra/esse/dist/js/types";

export type ReactionEnergyProfilePropertySchemaMixin = Omit<
    ReactionEnergyProfilePropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type ReactionEnergyProfilePropertyInMemoryEntity = InMemoryEntity &
    ReactionEnergyProfilePropertySchemaMixin;

export function reactionEnergyProfilePropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & ReactionEnergyProfilePropertySchemaMixin = {
        get xAxis() {
            return this.requiredProp<ReactionEnergyProfilePropertySchema["xAxis"]>("xAxis");
        },
        get yAxis() {
            return this.requiredProp<ReactionEnergyProfilePropertySchema["yAxis"]>("yAxis");
        },
        get name() {
            return this.requiredProp<ReactionEnergyProfilePropertySchema["name"]>("name");
        },
        get xDataArray() {
            return this.requiredProp<ReactionEnergyProfilePropertySchema["xDataArray"]>(
                "xDataArray",
            );
        },
        get yDataSeries() {
            return this.requiredProp<ReactionEnergyProfilePropertySchema["yDataSeries"]>(
                "yDataSeries",
            );
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
