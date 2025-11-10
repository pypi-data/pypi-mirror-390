/* eslint-disable class-methods-use-this */
import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { PhononBandStructurePropertySchema } from "@mat3ra/esse/dist/js/types";
import type { KPointPath } from "@mat3ra/made/dist/js/lattice/reciprocal/lattice_reciprocal";
import type { Options } from "highcharts";

import {
    PhononDispersionsPropertySchemaMixin,
    phononDispersionsPropertySchemaMixin,
} from "../../generated/PhononDispersionsPropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";
import { type XDataArrayNested } from "../include/mixins/2d_plot";
import { BandStructureConfig } from "./BandStructureProperty";

class PhononDispersionsConfig extends BandStructureConfig {
    tooltipFormatter(xDataArray: XDataArrayNested, yAxisName = "frequency") {
        return super.tooltipFormatter(xDataArray, yAxisName);
    }
}

type Schema = PhononBandStructurePropertySchema;
type Base = typeof Property<Schema> & Constructor<PhononDispersionsPropertySchemaMixin>;

class PhononDispersionsProperty extends (Property as Base) implements Schema {
    static readonly propertyName = PropertyName.phonon_dispersions;

    static readonly propertyType = PropertyType.non_scalar;

    readonly subtitle = "Phonon Dispersions";

    readonly yAxisTitle = `Frequency (${this.yAxis.units})`;

    readonly chartConfig: Options;

    constructor(config: Omit<Schema, "name"> & { pointsPath?: KPointPath }) {
        super({ ...config, name: PhononDispersionsProperty.propertyName });
        this.chartConfig = new PhononDispersionsConfig(this, {
            pointsPath: config.pointsPath,
        }).config;
    }
}

phononDispersionsPropertySchemaMixin(PhononDispersionsProperty.prototype);

export default PhononDispersionsProperty;
