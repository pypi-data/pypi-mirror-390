import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { HubbardVNNParametersPropertySchema } from "@mat3ra/esse/dist/js/types";

export type HubbardVNNPropertySchemaMixin = Omit<
    HubbardVNNParametersPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type HubbardVNNPropertyInMemoryEntity = InMemoryEntity & HubbardVNNPropertySchemaMixin;

export function hubbardVNNPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & HubbardVNNPropertySchemaMixin = {
        get name() {
            return this.requiredProp<HubbardVNNParametersPropertySchema["name"]>("name");
        },
        get units() {
            return this.requiredProp<HubbardVNNParametersPropertySchema["units"]>("units");
        },
        get values() {
            return this.requiredProp<HubbardVNNParametersPropertySchema["values"]>("values");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
