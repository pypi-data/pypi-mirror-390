import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { HubbardVParametersPropertySchema } from "@mat3ra/esse/dist/js/types";

export type HubbardVPropertySchemaMixin = Omit<
    HubbardVParametersPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type HubbardVPropertyInMemoryEntity = InMemoryEntity & HubbardVPropertySchemaMixin;

export function hubbardVPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & HubbardVPropertySchemaMixin = {
        get name() {
            return this.requiredProp<HubbardVParametersPropertySchema["name"]>("name");
        },
        get units() {
            return this.requiredProp<HubbardVParametersPropertySchema["units"]>("units");
        },
        get values() {
            return this.requiredProp<HubbardVParametersPropertySchema["values"]>("values");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
