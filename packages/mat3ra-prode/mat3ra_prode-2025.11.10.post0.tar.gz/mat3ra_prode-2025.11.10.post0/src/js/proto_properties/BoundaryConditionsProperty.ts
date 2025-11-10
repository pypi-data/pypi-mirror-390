import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { BoundaryConditionsPropertySchema } from "@mat3ra/esse/dist/js/types";

import {
    type BoundaryConditionsPropertySchemaMixin,
    boundaryConditionsPropertySchemaMixin,
} from "../generated/BoundaryConditionsPropertySchemaMixin";
import ProtoProperty from "../ProtoProperty";
import { PropertyName } from "../settings";

type Schema = BoundaryConditionsPropertySchema;

type Base = typeof ProtoProperty<Schema> & Constructor<BoundaryConditionsPropertySchemaMixin>;

class BoundaryConditionsProperty extends (ProtoProperty as Base) implements Schema {
    static readonly propertyName = PropertyName.boundary_conditions;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: BoundaryConditionsProperty.propertyName });
    }
}

boundaryConditionsPropertySchemaMixin(BoundaryConditionsProperty.prototype);

export default BoundaryConditionsProperty;
