import { deepClone, flattenObject } from "@mat3ra/code/dist/js/utils";
import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { BandGapsPropertySchema } from "@mat3ra/esse/dist/js/types";

import {
    type BandGapsPropertySchemaMixin,
    bandGapsPropertySchemaMixin,
} from "../../generated/BandGapsPropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";

type Schema = BandGapsPropertySchema;

type Base = typeof Property<Schema> & Constructor<BandGapsPropertySchemaMixin>;

export default class BandGapsProperty extends (Property as Base) implements Schema {
    static readonly isRefined = true;

    static readonly propertyName = PropertyName.band_gaps;

    static readonly propertyType = PropertyType.non_scalar;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: BandGapsProperty.propertyName });
    }

    toRowValues(group?: string) {
        return [this.toJSONByType("direct", group), this.toJSONByType("indirect", group)];
    }

    flattenProperties() {
        return this.values
            .map((x) => {
                return {
                    name: `${this.name}:${x.type}`,
                    value: x.value,
                };
            })
            .map((x) => flattenObject(x));
    }

    /**
     * @summary Gets specified band gap (direct/indirect) and returns it in simplified form (as pressure).
     * Characteristic name will be `band_gaps:<type>`
     * @param type {String}
     */
    private toJSONByType(type: string, group?: string) {
        const ch = this.toJSON();
        const bandGapByType = deepClone(ch) as BandGapsPropertySchema;
        const directData = this.values.find((x) => x.type === type);
        const name = `band_gaps:${type}`;

        return {
            ...bandGapByType,
            data: {
                ...directData,
                name,
            },
            slug: name,
            group,
        };
    }
}

bandGapsPropertySchemaMixin(BandGapsProperty.prototype);
