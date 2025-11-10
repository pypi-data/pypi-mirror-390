import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { FinalStructurePropertySchema } from "@mat3ra/esse/dist/js/types";

import {
    type FinalStructurePropertySchemaMixin,
    finalStructurePropertySchemaMixin,
} from "../../generated/FinalStructurePropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";

type Schema = FinalStructurePropertySchema;

type Base = typeof Property<Schema> & Constructor<FinalStructurePropertySchemaMixin>;

export default class FinalStructureProperty extends (Property as Base) implements Schema {
    static readonly propertyName = PropertyName.final_structure;

    static readonly propertyType = PropertyType.non_scalar;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: FinalStructureProperty.propertyName });
    }
}

finalStructurePropertySchemaMixin(FinalStructureProperty.prototype);
