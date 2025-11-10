import type { InMemoryEntity } from "@mat3ra/code/dist/js/entity";
import type { IonizationPotentialElementalPropertySchema } from "@mat3ra/esse/dist/js/types";

export type IonizationPotentialElementalPropertySchemaMixin = Omit<
    IonizationPotentialElementalPropertySchema,
    "_id" | "slug" | "systemName" | "schemaVersion"
>;

export type IonizationPotentialElementalPropertyInMemoryEntity = InMemoryEntity &
    IonizationPotentialElementalPropertySchemaMixin;

export function ionizationPotentialElementalPropertySchemaMixin(item: InMemoryEntity) {
    // @ts-expect-error
    const properties: InMemoryEntity & IonizationPotentialElementalPropertySchemaMixin = {
        get name() {
            return this.requiredProp<IonizationPotentialElementalPropertySchema["name"]>("name");
        },
        get units() {
            return this.requiredProp<IonizationPotentialElementalPropertySchema["units"]>("units");
        },
        get value() {
            return this.requiredProp<IonizationPotentialElementalPropertySchema["value"]>("value");
        },
    };

    Object.defineProperties(item, Object.getOwnPropertyDescriptors(properties));
}
