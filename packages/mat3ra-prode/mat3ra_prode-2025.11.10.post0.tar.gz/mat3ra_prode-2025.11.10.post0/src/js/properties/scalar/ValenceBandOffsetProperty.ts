import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { ValenceBandOffsetPropertySchema } from "@mat3ra/esse/dist/js/types";

import {
    ValenceBandOffsetPropertySchemaMixin,
    valenceBandOffsetPropertySchemaMixin,
} from "../../generated/ValenceBandOffsetPropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";

type Schema = ValenceBandOffsetPropertySchema;

type Base = typeof Property<Schema> & Constructor<ValenceBandOffsetPropertySchemaMixin>;

export default class ValenceBandOffsetProperty extends (Property as Base) implements Schema {
    static readonly isRefined = true;

    static readonly propertyName = PropertyName.valence_band_offset;

    static readonly propertyType = PropertyType.scalar;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: ValenceBandOffsetProperty.propertyName });
    }
}

valenceBandOffsetPropertySchemaMixin(ValenceBandOffsetProperty.prototype);
