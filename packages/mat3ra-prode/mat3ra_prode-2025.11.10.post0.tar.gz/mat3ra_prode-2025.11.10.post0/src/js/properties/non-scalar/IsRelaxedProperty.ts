import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { IsRelaxedPropertySchema } from "@mat3ra/esse/dist/js/types";

import {
    type IsRelaxedPropertySchemaMixin,
    isRelaxedPropertySchemaMixin,
} from "../../generated/IsRelaxedPropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";

type Schema = IsRelaxedPropertySchema;

type Base = typeof Property<Schema> & Constructor<IsRelaxedPropertySchemaMixin>;

export default class IsRelaxedProperty extends (Property as Base) implements Schema {
    static readonly isRefined = true;

    static readonly propertyName = PropertyName.is_relaxed;

    static readonly propertyType = PropertyType.non_scalar;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: IsRelaxedProperty.propertyName });
    }
}

isRelaxedPropertySchemaMixin(IsRelaxedProperty.prototype);
