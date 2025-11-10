import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { TotalEnergyPropertySchema } from "@mat3ra/esse/dist/js/types";

import {
    TotalEnergyPropertySchemaMixin,
    totalEnergyPropertySchemaMixin,
} from "../../generated/TotalEnergyPropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";

type Schema = TotalEnergyPropertySchema;

type Base = typeof Property<Schema> & Constructor<TotalEnergyPropertySchemaMixin>;

export default class TotalEnergyProperty extends (Property as Base) implements Schema {
    static readonly isRefined = true;

    static readonly propertyName = PropertyName.total_energy;

    static readonly propertyType = PropertyType.scalar;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: TotalEnergyProperty.propertyName });
    }
}

totalEnergyPropertySchemaMixin(TotalEnergyProperty.prototype);
