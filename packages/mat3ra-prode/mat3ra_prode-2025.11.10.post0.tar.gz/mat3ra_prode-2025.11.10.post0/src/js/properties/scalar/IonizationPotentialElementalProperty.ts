import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { IonizationPotentialElementalPropertySchema } from "@mat3ra/esse/dist/js/types";

import {
    IonizationPotentialElementalPropertySchemaMixin,
    ionizationPotentialElementalPropertySchemaMixin,
} from "../../generated/IonizationPotentialElementalPropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";

type Schema = IonizationPotentialElementalPropertySchema;

type Base = typeof Property<Schema> & Constructor<IonizationPotentialElementalPropertySchemaMixin>;

class IonizationPotentialElementalProperty extends (Property as Base) implements Schema {
    static readonly propertyName = PropertyName.ionization_potential;

    static readonly propertyType = PropertyType.scalar;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: IonizationPotentialElementalProperty.propertyName });
    }
}

ionizationPotentialElementalPropertySchemaMixin(IonizationPotentialElementalProperty.prototype);

export default IonizationPotentialElementalProperty;
