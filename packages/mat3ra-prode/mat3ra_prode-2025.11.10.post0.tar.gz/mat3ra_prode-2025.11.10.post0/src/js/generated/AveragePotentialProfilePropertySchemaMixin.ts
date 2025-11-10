import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { AveragePotentialProfilePropertySchema } from "@mat3ra/esse/dist/js/types";

export type AveragePotentialProfilePropertySchemaMixin = Omit<
    AveragePotentialProfilePropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type AveragePotentialProfilePropertyInMemoryEntity = InMemoryEntity &
    AveragePotentialProfilePropertySchemaMixin;

export function averagePotentialProfilePropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & AveragePotentialProfilePropertySchemaMixin = {
        get xAxis() {
            return this.requiredProp<AveragePotentialProfilePropertySchema["xAxis"]>("xAxis");
        },
        get yAxis() {
            return this.requiredProp<AveragePotentialProfilePropertySchema["yAxis"]>("yAxis");
        },
        get name() {
            return this.requiredProp<AveragePotentialProfilePropertySchema["name"]>("name");
        },
        get xDataArray() {
            return this.requiredProp<AveragePotentialProfilePropertySchema["xDataArray"]>(
                "xDataArray",
            );
        },
        get yDataSeries() {
            return this.requiredProp<AveragePotentialProfilePropertySchema["yDataSeries"]>(
                "yDataSeries",
            );
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
