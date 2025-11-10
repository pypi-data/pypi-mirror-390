import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { HubbardUParametersPropertySchema } from "@mat3ra/esse/dist/js/types";

import {
    type HubbardUPropertySchemaMixin,
    hubbardUPropertySchemaMixin,
} from "../../generated/HubbardUPropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";

type Schema = HubbardUParametersPropertySchema;

type Base = typeof Property<Schema> & Constructor<HubbardUPropertySchemaMixin>;

export default class HubbardUProperty extends (Property as Base) implements Schema {
    static readonly propertyName = PropertyName.hubbard_u;

    static readonly propertyType = PropertyType.non_scalar;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: HubbardUProperty.propertyName });
    }
}

hubbardUPropertySchemaMixin(HubbardUProperty.prototype);
