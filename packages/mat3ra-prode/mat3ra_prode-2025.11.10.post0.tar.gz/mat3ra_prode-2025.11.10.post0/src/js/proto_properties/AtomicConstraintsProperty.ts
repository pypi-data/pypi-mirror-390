import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { AtomicConstraintsPropertySchema } from "@mat3ra/esse/dist/js/types";

import {
    type AtomicConstraintsPropertySchemaMixin,
    atomicConstraintsPropertySchemaMixin,
} from "../generated/AtomicConstraintsPropertySchemaMixin";
import ProtoProperty from "../ProtoProperty";
import { PropertyName } from "../settings";

type Schema = AtomicConstraintsPropertySchema;

type Base = typeof ProtoProperty<Schema> & Constructor<AtomicConstraintsPropertySchemaMixin>;

class AtomicConstraintsProperty extends (ProtoProperty as Base) implements Schema {
    static readonly propertyName = PropertyName.atomic_constraints;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: AtomicConstraintsProperty.propertyName });
    }
}

atomicConstraintsPropertySchemaMixin(AtomicConstraintsProperty.prototype);

export default AtomicConstraintsProperty;
