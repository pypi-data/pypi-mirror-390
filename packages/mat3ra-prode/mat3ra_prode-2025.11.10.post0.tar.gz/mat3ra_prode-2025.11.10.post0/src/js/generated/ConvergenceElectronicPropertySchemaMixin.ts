import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { ConvergenceElectronicPropertySchema } from "@mat3ra/esse/dist/js/types";

export type ConvergenceElectronicPropertySchemaMixin = Omit<
    ConvergenceElectronicPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type ConvergenceElectronicPropertyInMemoryEntity = InMemoryEntity &
    ConvergenceElectronicPropertySchemaMixin;

export function convergenceElectronicPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & ConvergenceElectronicPropertySchemaMixin = {
        get name() {
            return this.requiredProp<ConvergenceElectronicPropertySchema["name"]>("name");
        },
        get units() {
            return this.requiredProp<ConvergenceElectronicPropertySchema["units"]>("units");
        },
        get data() {
            return this.requiredProp<ConvergenceElectronicPropertySchema["data"]>("data");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
