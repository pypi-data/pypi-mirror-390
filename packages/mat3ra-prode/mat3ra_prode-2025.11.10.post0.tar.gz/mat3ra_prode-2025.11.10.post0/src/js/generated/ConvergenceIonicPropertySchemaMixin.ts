import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { ConvergenceIonicPropertySchema } from "@mat3ra/esse/dist/js/types";

export type ConvergenceIonicPropertySchemaMixin = Omit<
    ConvergenceIonicPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type ConvergenceIonicPropertyInMemoryEntity = InMemoryEntity &
    ConvergenceIonicPropertySchemaMixin;

export function convergenceIonicPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & ConvergenceIonicPropertySchemaMixin = {
        get name() {
            return this.requiredProp<ConvergenceIonicPropertySchema["name"]>("name");
        },
        get tolerance() {
            return this.prop<ConvergenceIonicPropertySchema["tolerance"]>("tolerance");
        },
        get units() {
            return this.requiredProp<ConvergenceIonicPropertySchema["units"]>("units");
        },
        get data() {
            return this.requiredProp<ConvergenceIonicPropertySchema["data"]>("data");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
