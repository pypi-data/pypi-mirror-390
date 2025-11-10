import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { TotalEnergyContributionsPropertySchema } from "@mat3ra/esse/dist/js/types";

import {
    TotalEnergyContributionsPropertySchemaMixin,
    totalEnergyContributionsPropertySchemaMixin,
} from "../../generated/TotalEnergyContributionsPropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";

type Schema = TotalEnergyContributionsPropertySchema;

type Base = typeof Property<Schema> & Constructor<TotalEnergyContributionsPropertySchemaMixin>;

export default class TotalEnergyContributionsProperty extends (Property as Base) implements Schema {
    static readonly propertyType = PropertyType.object;

    static readonly propertyName = PropertyName.total_energy_contributions;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: TotalEnergyContributionsProperty.propertyName });
    }

    get exchangeCorrelation() {
        return this.exchange_correlation;
    }
}

totalEnergyContributionsPropertySchemaMixin(TotalEnergyContributionsProperty.prototype);
