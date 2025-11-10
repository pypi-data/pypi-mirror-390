import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { StressTensorPropertySchema } from "@mat3ra/esse/dist/js/types";

export type StressTensorPropertySchemaMixin = Omit<
    StressTensorPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type StressTensorPropertyInMemoryEntity = InMemoryEntity & StressTensorPropertySchemaMixin;

export function stressTensorPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & StressTensorPropertySchemaMixin = {
        get value() {
            return this.requiredProp<StressTensorPropertySchema["value"]>("value");
        },
        get name() {
            return this.requiredProp<StressTensorPropertySchema["name"]>("name");
        },
        get units() {
            return this.requiredProp<StressTensorPropertySchema["units"]>("units");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
