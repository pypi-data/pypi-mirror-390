import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { TotalForcesPropertySchema } from "@mat3ra/esse/dist/js/types";

import {
    TotalForcePropertySchemaMixin,
    totalForcePropertySchemaMixin,
} from "../../generated/TotalForcePropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";

type Schema = TotalForcesPropertySchema;

type Base = typeof Property<Schema> & Constructor<TotalForcePropertySchemaMixin>;

export default class TotalForceProperty extends (Property as Base) implements Schema {
    static readonly propertyName = PropertyName.total_force;

    static readonly propertyType = PropertyType.scalar;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: TotalForceProperty.propertyName });
    }
}

totalForcePropertySchemaMixin(TotalForceProperty.prototype);
