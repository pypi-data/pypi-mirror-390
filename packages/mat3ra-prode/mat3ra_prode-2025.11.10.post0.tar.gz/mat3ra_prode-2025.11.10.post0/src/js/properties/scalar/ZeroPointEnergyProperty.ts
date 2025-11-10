import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { ZeroPointEnergyPropertySchema } from "@mat3ra/esse/dist/js/types";

import {
    ZeroPointEnergyPropertySchemaMixin,
    zeroPointEnergyPropertySchemaMixin,
} from "../../generated/ZeroPointEnergyPropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";

type Schema = ZeroPointEnergyPropertySchema;

type Base = typeof Property<Schema> & Constructor<ZeroPointEnergyPropertySchemaMixin>;

export default class ZeroPointEnergyProperty extends (Property as Base) implements Schema {
    static readonly propertyName = PropertyName.zero_point_energy;

    static readonly propertyType = PropertyType.scalar;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: ZeroPointEnergyProperty.propertyName });
    }
}

zeroPointEnergyPropertySchemaMixin(ZeroPointEnergyProperty.prototype);
