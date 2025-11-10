import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { MagneticMomentsPropertySchema } from "@mat3ra/esse/dist/js/types";

import {
    MagneticMomentsPropertySchemaMixin,
    magneticMomentsPropertySchemaMixin,
} from "../../generated/MagneticMomentsPropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";

type Schema = MagneticMomentsPropertySchema;

type Base = typeof Property<Schema> & Constructor<MagneticMomentsPropertySchemaMixin>;

class MagneticMomentsProperty extends (Property as Base) implements Schema {
    static readonly propertyName = PropertyName.magnetic_moments;

    static readonly propertyType = PropertyType.tensor;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: MagneticMomentsProperty.propertyName });
    }
}

magneticMomentsPropertySchemaMixin(MagneticMomentsProperty.prototype);

export default MagneticMomentsProperty;
