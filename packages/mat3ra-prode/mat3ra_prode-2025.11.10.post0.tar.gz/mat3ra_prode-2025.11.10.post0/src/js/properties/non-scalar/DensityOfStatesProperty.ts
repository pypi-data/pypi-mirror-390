/* eslint-disable class-methods-use-this */
/* eslint-disable max-classes-per-file */
import type { Constructor } from "@mat3ra/code/dist/js/utils/types.js";
import type { DensityOfStatesPropertySchema } from "@mat3ra/esse/dist/js/types";
import type { IndividualSeriesOptions, Options } from "highcharts";
import zip from "lodash/zip";

import { type FormatterScope, HighChartsConfig } from "../../charts/highcharts";
import {
    type DensityOfStatesPropertySchemaMixin,
    densityOfStatesPropertySchemaMixin,
} from "../../generated/DensityOfStatesPropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";
import { type YDataSeries } from "../include/mixins/2d_plot";

type Schema = DensityOfStatesPropertySchema;

export class DensityOfStatesConfig extends HighChartsConfig {
    readonly yDataSeries: YDataSeries;

    readonly fermiEnergy: number | null;

    readonly xDataArray: Schema["xDataArray"];

    readonly legends: Schema["legend"];

    get overrideConfig() {
        return {
            colors: [
                "#7cb5ec",
                "#90ed7d",
                "#f7a35c",
                "#8085e9",
                "#f15c80",
                "#e4d354",
                "#2b908f",
                "#f45b5b",
                "#91e8e1",
            ],
            credits: {
                enabled: false,
            },
            chart: {
                type: "spline",
                zoomType: "xy",
                animation: false,
            },
            legend: {
                layout: "horizontal",
                align: "center",
                verticalAlign: "bottom",
                borderWidth: 0,
            },
        };
    }

    constructor(
        property: {
            subtitle: string;
            yAxisTitle: string;
            xAxisTitle: string;
            yDataSeries: YDataSeries;
            legend?: Schema["legend"];
            xDataArray: Schema["xDataArray"];
        },
        chartConfig?: {
            fermiEnergy?: number | null;
        },
    ) {
        super({
            subtitle: property.subtitle,
            yAxisTitle: property.yAxisTitle,
            xAxisTitle: property.xAxisTitle,
            yAxisType: "linear",
        });

        this.yDataSeries = property.yDataSeries;
        this.legends = property.legend || [];
        this.fermiEnergy = chartConfig?.fermiEnergy ?? 0;
        this.xDataArray = this.cleanXDataArray(property.xDataArray);
    }

    // shifting values wrt fermi energy here
    cleanXDataArray(rawData: Schema["xDataArray"]) {
        return rawData.flat().map((x) => {
            const value = this.fermiEnergy ? x - this.fermiEnergy : x;
            return Number(value.toPrecision(4));
        });
    }

    get series(): IndividualSeriesOptions[] {
        return this.yDataSeries.map((item, index) => {
            const legend = this.legends[index];
            const spinText = legend?.spin ? ` ${legend.spin > 0 ? "↑" : "↓"}` : "";
            const name = legend?.element
                ? `${legend.element} ${legend.electronicState}${spinText}`
                : "Total";

            return {
                data: zip(
                    this.xDataArray,
                    item.map((x) => Number(Number(x).toPrecision(4))),
                ) as IndividualSeriesOptions["data"],
                name,
                color: name === "Total" ? "#000000" : undefined,
                animation: false,
            };
        });
    }

    tooltipFormatter() {
        // eslint-disable-next-line func-names
        return function (this: FormatterScope) {
            return (
                "<b>state:</b> " +
                this.series.name +
                "<br>" +
                "<b>energy:</b> " +
                this.key.toFixed(4) +
                "<br>" +
                "<b>value: </b>  " +
                this.y.toFixed(4)
            );
        };
    }

    xAxis() {
        return {
            ...super.xAxis(),
            plotLines: this.fermiEnergy
                ? this.plotSingleLine({
                      value: 0.0,
                      label: {
                          text: "E_F",
                          style: {
                              color: "red",
                          },
                          y: 15,
                          x: 5,
                          rotation: 0,
                      },
                  })
                : [],
        };
    }
}

type Base = typeof Property<Schema> & Constructor<DensityOfStatesPropertySchemaMixin>;

export default class DensityOfStatesProperty extends (Property as Base) implements Schema {
    readonly subtitle: string = "Density Of States";

    readonly yAxisTitle: string = `Density Of States (${this.yAxis.units})`;

    readonly xAxisTitle: string = `Energy (${this.xAxis.units})`;

    readonly chartConfig: Options;

    static readonly isRefined = true;

    static readonly propertyName = PropertyName.density_of_states;

    static readonly propertyType = PropertyType.non_scalar;

    constructor(config: Omit<Schema, "name"> & { fermiEnergy?: number | null }) {
        super({ ...config, name: DensityOfStatesProperty.propertyName });
        this.chartConfig = new DensityOfStatesConfig(this, {
            fermiEnergy: config.fermiEnergy,
        }).config;
    }
}

densityOfStatesPropertySchemaMixin(DensityOfStatesProperty.prototype);
