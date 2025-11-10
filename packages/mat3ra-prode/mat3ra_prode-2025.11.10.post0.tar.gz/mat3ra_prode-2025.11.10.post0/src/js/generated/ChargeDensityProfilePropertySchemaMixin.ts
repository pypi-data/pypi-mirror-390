import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { ChargeDensityProfilePropertySchema } from "@mat3ra/esse/dist/js/types";

export type ChargeDensityProfilePropertySchemaMixin = Omit<
    ChargeDensityProfilePropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type ChargeDensityProfilePropertyInMemoryEntity = InMemoryEntity &
    ChargeDensityProfilePropertySchemaMixin;

export function chargeDensityProfilePropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & ChargeDensityProfilePropertySchemaMixin = {
        get xAxis() {
            return this.requiredProp<ChargeDensityProfilePropertySchema["xAxis"]>("xAxis");
        },
        get yAxis() {
            return this.requiredProp<ChargeDensityProfilePropertySchema["yAxis"]>("yAxis");
        },
        get name() {
            return this.requiredProp<ChargeDensityProfilePropertySchema["name"]>("name");
        },
        get xDataArray() {
            return this.requiredProp<ChargeDensityProfilePropertySchema["xDataArray"]>(
                "xDataArray",
            );
        },
        get yDataSeries() {
            return this.requiredProp<ChargeDensityProfilePropertySchema["yDataSeries"]>(
                "yDataSeries",
            );
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
