import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { HubbardVNNParametersPropertySchema } from "@mat3ra/esse/dist/js/types";

import {
    type HubbardVNNPropertySchemaMixin,
    hubbardVNNPropertySchemaMixin,
} from "../../generated/HubbardVNNPropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";

type Schema = HubbardVNNParametersPropertySchema;

type Base = typeof Property<Schema> & Constructor<HubbardVNNPropertySchemaMixin>;

export default class HubbardVNNProperty extends (Property as Base) implements Schema {
    static readonly propertyName = PropertyName.hubbard_v_nn;

    static readonly propertyType = PropertyType.non_scalar;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: HubbardVNNProperty.propertyName });
    }
}

hubbardVNNPropertySchemaMixin(HubbardVNNProperty.prototype);
