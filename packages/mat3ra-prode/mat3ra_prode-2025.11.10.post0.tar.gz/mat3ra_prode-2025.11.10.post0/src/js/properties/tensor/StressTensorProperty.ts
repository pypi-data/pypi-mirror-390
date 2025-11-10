import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { StressTensorPropertySchema } from "@mat3ra/esse/dist/js/types";

import {
    StressTensorPropertySchemaMixin,
    stressTensorPropertySchemaMixin,
} from "../../generated/StressTensorPropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";

type Schema = StressTensorPropertySchema;

type Base = typeof Property<Schema> & Constructor<StressTensorPropertySchemaMixin>;

export default class StressTensorProperty extends (Property as Base) implements Schema {
    static readonly propertyName = PropertyName.stress_tensor;

    static readonly propertyType = PropertyType.tensor;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: StressTensorProperty.propertyName });
    }
}

stressTensorPropertySchemaMixin(StressTensorProperty.prototype);
