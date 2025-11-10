/* eslint-disable class-methods-use-this */
/* eslint-disable max-classes-per-file */

import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { ChargeDensityProfilePropertySchema } from "@mat3ra/esse/dist/js/types";
import type { Options } from "highcharts";

import {
    type ChargeDensityProfilePropertySchemaMixin,
    chargeDensityProfilePropertySchemaMixin,
} from "../../generated/ChargeDensityProfilePropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";
import { TwoDimensionalHighChartConfigMixin } from "../include/mixins/2d_plot";

export class ChargeDensityProfileConfig extends TwoDimensionalHighChartConfigMixin {
    readonly tooltipXAxisName = "z coordinate";

    readonly tooltipYAxisName = "charge density";
}

type Schema = ChargeDensityProfilePropertySchema;

type Base = typeof Property<Schema> & Constructor<ChargeDensityProfilePropertySchemaMixin>;

class ChargeDensityProfileProperty extends (Property as Base) implements Schema {
    readonly subtitle: string = "Charge Density Profile";

    readonly yAxisTitle: string = `Charge Density (${this.yAxis.units})`;

    readonly xAxisTitle: string = "Z Coordinate";

    readonly chartConfig: Options = new ChargeDensityProfileConfig(this).config;

    static readonly isRefined = true;

    static readonly propertyName = PropertyName.charge_density_profile;

    static readonly propertyType = PropertyType.non_scalar;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: ChargeDensityProfileProperty.propertyName });
    }
}

chargeDensityProfilePropertySchemaMixin(ChargeDensityProfileProperty.prototype);

export default ChargeDensityProfileProperty;
