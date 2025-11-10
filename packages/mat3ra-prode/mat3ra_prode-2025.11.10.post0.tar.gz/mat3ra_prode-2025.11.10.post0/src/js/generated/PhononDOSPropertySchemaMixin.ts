import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { PhononDensityOfStatesPropertySchema } from "@mat3ra/esse/dist/js/types";

export type PhononDOSPropertySchemaMixin = Omit<
    PhononDensityOfStatesPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type PhononDOSPropertyInMemoryEntity = InMemoryEntity & PhononDOSPropertySchemaMixin;

export function phononDOSPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & PhononDOSPropertySchemaMixin = {
        get xAxis() {
            return this.requiredProp<PhononDensityOfStatesPropertySchema["xAxis"]>("xAxis");
        },
        get yAxis() {
            return this.requiredProp<PhononDensityOfStatesPropertySchema["yAxis"]>("yAxis");
        },
        get name() {
            return this.requiredProp<PhononDensityOfStatesPropertySchema["name"]>("name");
        },
        get xDataArray() {
            return this.requiredProp<PhononDensityOfStatesPropertySchema["xDataArray"]>(
                "xDataArray",
            );
        },
        get yDataSeries() {
            return this.requiredProp<PhononDensityOfStatesPropertySchema["yDataSeries"]>(
                "yDataSeries",
            );
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
