/* eslint-disable max-classes-per-file */
import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { AveragePotentialProfilePropertySchema } from "@mat3ra/esse/dist/js/types";
import type { Options } from "highcharts";
import zip from "lodash/zip";

import {
    type AveragePotentialProfilePropertySchemaMixin,
    averagePotentialProfilePropertySchemaMixin,
} from "../../generated/AveragePotentialProfilePropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";
import { TwoDimensionalHighChartConfigMixin } from "../include/mixins/2d_plot";

const NAMES = ["planar average", "macroscopic average"];

export class AveragePotentialProfileConfig extends TwoDimensionalHighChartConfigMixin {
    readonly tooltipXAxisName: string = "z coordinate";

    readonly tooltipYAxisName: string = "energy";

    get series() {
        return this.yDataSeries.map((item, index) => {
            return {
                animation: false,
                name: NAMES[index],
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

type Schema = AveragePotentialProfilePropertySchema;

type Base = typeof Property<Schema> & Constructor<AveragePotentialProfilePropertySchemaMixin>;

export default class AveragePotentialProfileProperty extends (Property as Base) implements Schema {
    readonly subtitle: string = "Average Potential Profile";

    readonly yAxisTitle: string = `Energy (${this.yAxis.units})`;

    readonly xAxisTitle: string = `Coordinate (${this.xAxis.units})`;

    readonly chartConfig: Options = new AveragePotentialProfileConfig(this).config;

    static readonly isRefined = true;

    static readonly propertyName = PropertyName.average_potential_profile;

    static readonly propertyType = PropertyType.non_scalar;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: AveragePotentialProfileProperty.propertyName });
    }
}

averagePotentialProfilePropertySchemaMixin(AveragePotentialProfileProperty.prototype);
