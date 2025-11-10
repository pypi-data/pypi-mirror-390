import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { DensityOfStatesPropertySchema } from "@mat3ra/esse/dist/js/types";

export type DensityOfStatesPropertySchemaMixin = Omit<
    DensityOfStatesPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type DensityOfStatesPropertyInMemoryEntity = InMemoryEntity &
    DensityOfStatesPropertySchemaMixin;

export function densityOfStatesPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & DensityOfStatesPropertySchemaMixin = {
        get xAxis() {
            return this.requiredProp<DensityOfStatesPropertySchema["xAxis"]>("xAxis");
        },
        get yAxis() {
            return this.requiredProp<DensityOfStatesPropertySchema["yAxis"]>("yAxis");
        },
        get name() {
            return this.requiredProp<DensityOfStatesPropertySchema["name"]>("name");
        },
        get legend() {
            return this.requiredProp<DensityOfStatesPropertySchema["legend"]>("legend");
        },
        get xDataArray() {
            return this.requiredProp<DensityOfStatesPropertySchema["xDataArray"]>("xDataArray");
        },
        get yDataSeries() {
            return this.requiredProp<DensityOfStatesPropertySchema["yDataSeries"]>("yDataSeries");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
