/* eslint-disable class-methods-use-this */
/* eslint-disable max-classes-per-file */
import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { PotentialProfilePropertySchema } from "@mat3ra/esse/dist/js/types";
import type { Options } from "highcharts";
import zip from "lodash/zip";

import {
    PotentialProfilePropertySchemaMixin,
    potentialProfilePropertySchemaMixin,
} from "../../generated/PotentialProfilePropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";
import { TwoDimensionalHighChartConfigMixin } from "../include/mixins/2d_plot";

const NAMES = {
    0: "averageVHartree",
    1: "averageVLocal",
    2: "averageVHartreePlusLocal",
};

type Schema = PotentialProfilePropertySchema;

export class PotentialProfileConfig extends TwoDimensionalHighChartConfigMixin {
    readonly tooltipXAxisName: string = "z coordinate";

    readonly tooltipYAxisName: string = "energy";

    get series() {
        return this.yDataSeries.map((item, index) => {
            return {
                animation: false,
                name: NAMES[index as keyof typeof NAMES],
                data: zip(this.xDataArray, item) as [number, number][],
            };
        });
    }

    get overrideConfig() {
        return {
            ...super.overrideConfig,
            legend: {
                layout: "horizontal",
                align: "center",
                verticalAlign: "bottom",
                borderWidth: 0,
            },
        };
    }
}

type Base = typeof Property<Schema> & Constructor<PotentialProfilePropertySchemaMixin>;

class PotentialProfileProperty extends (Property as Base) implements Schema {
    readonly subtitle: string = "Potential Profile";

    readonly yAxisTitle: string = `Energy (${this.yAxis.units})`;

    readonly xAxisTitle: string = "Z Coordinate";

    readonly chartConfig: Options = new PotentialProfileConfig(this).config;

    static readonly isRefined = true;

    static readonly propertyName = PropertyName.potential_profile;

    static readonly propertyType = PropertyType.non_scalar;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: PotentialProfileProperty.propertyName });
    }
}

potentialProfilePropertySchemaMixin(PotentialProfileProperty.prototype);

export default PotentialProfileProperty;
