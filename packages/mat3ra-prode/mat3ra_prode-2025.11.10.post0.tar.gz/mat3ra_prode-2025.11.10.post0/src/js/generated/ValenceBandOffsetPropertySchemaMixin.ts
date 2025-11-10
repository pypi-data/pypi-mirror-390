import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { ValenceBandOffsetPropertySchema } from "@mat3ra/esse/dist/js/types";

export type ValenceBandOffsetPropertySchemaMixin = Omit<
    ValenceBandOffsetPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type ValenceBandOffsetPropertyInMemoryEntity = InMemoryEntity &
    ValenceBandOffsetPropertySchemaMixin;

export function valenceBandOffsetPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & ValenceBandOffsetPropertySchemaMixin = {
        get name() {
            return this.requiredProp<ValenceBandOffsetPropertySchema["name"]>("name");
        },
        get units() {
            return this.requiredProp<ValenceBandOffsetPropertySchema["units"]>("units");
        },
        get value() {
            return this.requiredProp<ValenceBandOffsetPropertySchema["value"]>("value");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
