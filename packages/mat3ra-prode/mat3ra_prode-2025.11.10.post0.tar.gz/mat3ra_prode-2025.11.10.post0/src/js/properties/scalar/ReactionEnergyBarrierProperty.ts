import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { ReactionEnergyBarrierPropertySchema } from "@mat3ra/esse/dist/js/types";

import {
    ReactionEnergyBarrierPropertySchemaMixin,
    reactionEnergyBarrierPropertySchemaMixin,
} from "../../generated/ReactionEnergyBarrierPropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";

type Schema = ReactionEnergyBarrierPropertySchema;

type Base = typeof Property<Schema> & Constructor<ReactionEnergyBarrierPropertySchemaMixin>;

class ReactionEnergyBarrierProperty extends (Property as Base) implements Schema {
    static readonly isRefined = true;

    static readonly propertyName = PropertyName.reaction_energy_barrier;

    static readonly propertyType = PropertyType.scalar;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: ReactionEnergyBarrierProperty.propertyName });
    }
}

reactionEnergyBarrierPropertySchemaMixin(ReactionEnergyBarrierProperty.prototype);

export default ReactionEnergyBarrierProperty;
