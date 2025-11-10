import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { PhononBandStructurePropertySchema } from "@mat3ra/esse/dist/js/types";

export type PhononDispersionsPropertySchemaMixin = Omit<
    PhononBandStructurePropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type PhononDispersionsPropertyInMemoryEntity = InMemoryEntity &
    PhononDispersionsPropertySchemaMixin;

export function phononDispersionsPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & PhononDispersionsPropertySchemaMixin = {
        get xAxis() {
            return this.requiredProp<PhononBandStructurePropertySchema["xAxis"]>("xAxis");
        },
        get yAxis() {
            return this.requiredProp<PhononBandStructurePropertySchema["yAxis"]>("yAxis");
        },
        get name() {
            return this.requiredProp<PhononBandStructurePropertySchema["name"]>("name");
        },
        get xDataArray() {
            return this.requiredProp<PhononBandStructurePropertySchema["xDataArray"]>("xDataArray");
        },
        get yDataSeries() {
            return this.requiredProp<PhononBandStructurePropertySchema["yDataSeries"]>(
                "yDataSeries",
            );
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
