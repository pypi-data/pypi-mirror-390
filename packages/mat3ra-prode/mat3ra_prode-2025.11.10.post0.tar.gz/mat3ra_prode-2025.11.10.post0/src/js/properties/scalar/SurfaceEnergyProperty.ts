import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { SurfaceEnergyPropertySchema } from "@mat3ra/esse/dist/js/types";

import {
    SurfaceEnergyPropertySchemaMixin,
    surfaceEnergyPropertySchemaMixin,
} from "../../generated/SurfaceEnergyPropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";

type Schema = SurfaceEnergyPropertySchema;

type Base = typeof Property<Schema> & Constructor<SurfaceEnergyPropertySchemaMixin>;

export default class SurfaceEnergyProperty extends (Property as Base) implements Schema {
    static readonly isRefined = true;

    static readonly propertyName = PropertyName.surface_energy;

    static readonly propertyType = PropertyType.scalar;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: SurfaceEnergyProperty.propertyName });
    }
}

surfaceEnergyPropertySchemaMixin(SurfaceEnergyProperty.prototype);
