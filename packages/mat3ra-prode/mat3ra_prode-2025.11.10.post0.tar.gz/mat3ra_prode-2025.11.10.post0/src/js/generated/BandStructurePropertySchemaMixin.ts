import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { BandStructurePropertySchema } from "@mat3ra/esse/dist/js/types";

export type BandStructurePropertySchemaMixin = Omit<
    BandStructurePropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type BandStructurePropertyInMemoryEntity = InMemoryEntity & BandStructurePropertySchemaMixin;

export function bandStructurePropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & BandStructurePropertySchemaMixin = {
        get xAxis() {
            return this.requiredProp<BandStructurePropertySchema["xAxis"]>("xAxis");
        },
        get yAxis() {
            return this.requiredProp<BandStructurePropertySchema["yAxis"]>("yAxis");
        },
        get name() {
            return this.requiredProp<BandStructurePropertySchema["name"]>("name");
        },
        get spin() {
            return this.requiredProp<BandStructurePropertySchema["spin"]>("spin");
        },
        get xDataArray() {
            return this.requiredProp<BandStructurePropertySchema["xDataArray"]>("xDataArray");
        },
        get yDataSeries() {
            return this.requiredProp<BandStructurePropertySchema["yDataSeries"]>("yDataSeries");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
