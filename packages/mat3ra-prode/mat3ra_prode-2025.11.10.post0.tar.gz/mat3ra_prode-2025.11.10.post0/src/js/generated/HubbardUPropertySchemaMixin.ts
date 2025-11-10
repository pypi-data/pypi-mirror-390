import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { HubbardUParametersPropertySchema } from "@mat3ra/esse/dist/js/types";

export type HubbardUPropertySchemaMixin = Omit<
    HubbardUParametersPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type HubbardUPropertyInMemoryEntity = InMemoryEntity & HubbardUPropertySchemaMixin;

export function hubbardUPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & HubbardUPropertySchemaMixin = {
        get name() {
            return this.requiredProp<HubbardUParametersPropertySchema["name"]>("name");
        },
        get units() {
            return this.requiredProp<HubbardUParametersPropertySchema["units"]>("units");
        },
        get values() {
            return this.requiredProp<HubbardUParametersPropertySchema["values"]>("values");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
