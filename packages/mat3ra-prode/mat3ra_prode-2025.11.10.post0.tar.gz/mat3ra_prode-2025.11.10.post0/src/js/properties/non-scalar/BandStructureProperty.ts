/* eslint-disable class-methods-use-this */
// eslint-disable-next-line max-classes-per-file
import { math as codeJSMath } from "@mat3ra/code/dist/js/math";
import { deepClone } from "@mat3ra/code/dist/js/utils";
import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { BandStructurePropertySchema } from "@mat3ra/esse/dist/js/types";
import type { KPointPath } from "@mat3ra/made/dist/js/lattice/reciprocal/lattice_reciprocal";
import type { Options, PlotLines } from "highcharts";
import zip from "lodash/zip";

import { type FormatterScope, HighChartsConfig } from "../../charts/highcharts";
import {
    type BandStructurePropertySchemaMixin,
    bandStructurePropertySchemaMixin,
} from "../../generated/BandStructurePropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";
import {
    type XDataArray,
    type XDataArrayNested,
    type YDataSeries,
} from "../include/mixins/2d_plot";

export const _POINT_COORDINATES_PRECISION_ = 4; // number of decimals to keep for point coordinates

export class BandStructureConfig extends HighChartsConfig {
    readonly yDataSeries: YDataSeries;

    readonly spin?: number[];

    readonly xDataArray: XDataArrayNested;

    readonly pointsDistanceArray: number[];

    readonly fermiEnergy: number | null;

    readonly pointsPath: KPointPath | undefined;

    constructor(
        property: {
            spin?: number[];
            subtitle: string;
            yAxisTitle: string;
            yDataSeries: [number, ...number[]][];
            xDataArray: (number | number[])[];
        },
        chartConfig?: {
            fermiEnergy?: number | null;
            pointsPath?: KPointPath;
        },
    ) {
        super({
            subtitle: property.subtitle,
            yAxisTitle: property.yAxisTitle,
            yAxisType: "linear",
        });

        this.yDataSeries = property.yDataSeries;
        this.spin = property.spin;
        this.xDataArray = this.cleanXDataArray(property.xDataArray);

        this.pointsPath = chartConfig?.pointsPath;
        this.pointsDistanceArray = this.calculatePointsDistance(this.xDataArray);

        this.fermiEnergy = chartConfig?.fermiEnergy ?? null;

        this.plotXLineAtPoint = this.plotXLineAtPoint.bind(this);
        this.plotXLines = this.plotXLines.bind(this);
    }

    // round each value in array to certain precision
    cleanXDataArray(rawData: XDataArray = []): XDataArrayNested {
        return rawData.map((p) => {
            if (!p || !Array.isArray(p)) return [];

            return p.map((c) => {
                return codeJSMath.roundValueToNDecimals(c, _POINT_COORDINATES_PRECISION_);
            });
        });
    }

    // returns the array of distances calculated from an array of points
    calculatePointsDistance(listOfPoints: XDataArrayNested = []) {
        let pointsDistanceSum = 0;
        return listOfPoints.map((el, idx, arr) => {
            if (idx !== 0) {
                const distance = codeJSMath.vDist(el, arr[idx - 1]);
                pointsDistanceSum += Number(distance);
            }
            return pointsDistanceSum;
        });
    }

    // find index of a point inside an array of points
    findSymmetryPointIndex(xDataArray: XDataArrayNested, point: number[]) {
        return xDataArray.findIndex((p) => codeJSMath.vDist(p, point) === 0);
    }

    // create config for vertical lines at high symmetry points
    plotXLines(): PlotLines[] {
        const copiedXDataArray = deepClone(this.xDataArray);
        return this.pointsPath
            ? this.pointsPath
                  .map((p) => {
                      const idx = this.findSymmetryPointIndex(copiedXDataArray, p.coordinates);
                      // "reset" element at index if found to avoid duplicate matches
                      if (idx > -1) copiedXDataArray[idx] = [-1, -1, -1];
                      return {
                          point: p.point,
                          distance: idx > -1 ? this.pointsDistanceArray[idx] : null,
                      };
                  })
                  .map(this.plotXLineAtPoint)
            : [];
    }

    plotXLineAtPoint({ point, distance }: { point: string; distance: number | null }): PlotLines {
        return {
            label: {
                verticalAlign: "bottom",
                rotation: 0,
                align: "center",
                y: 20,
                x: 0,
                text: point,
            },
            value: distance ?? undefined,
            width: 1,
            dashStyle: "solid",
            color: "#E0E0E0",
        };
    }

    get series() {
        const { fermiEnergy } = this;

        const series_ = this.yDataSeries.map((item, index) => {
            // shift values by fermiEnergy
            const itemUpdated = item.map((x) => {
                return fermiEnergy ? Number(x) - fermiEnergy : Number(x);
            });

            const spin = this.spin?.[index];
            const spinText = spin && spin > 0 ? "up" : "down";

            return {
                data: zip(this.pointsDistanceArray, itemUpdated) as [number, number][],
                name: spinText,
                color: spinText === "up" ? "#3677d9" : "#ff7f0e",
                animation: false,
            };
        });

        return series_;
    }

    xAxis() {
        return {
            minorGridLineColor: "#E0E0E0",
            minorGridLineWidth: 2,
            minorTickLength: 0,
            title: {
                text: "Path in reciprocal space",
                offset: 40,
            },
            type: "linear",
            tickPositioner: () => [], // disable ticks
            plotLines: this.pointsPath ? this.plotXLines() : undefined,
            labels: {
                enabled: false,
            },
        };
    }

    tooltipFormatter(xDataArray: XDataArrayNested, yAxisName = "energy") {
        // note 'this' below refers to Highcharts tooltip scope
        // eslint-disable-next-line func-names
        return function (this: FormatterScope) {
            return (
                "<b>spin:</b> " +
                this.series.name +
                "<br>" +
                "<b>point:</b> " +
                xDataArray.map((p) => {
                    if (!Array.isArray(p)) {
                        console.error("xDataArray is not a nested array", xDataArray);
                        return [];
                    }
                    return p.map((c) => c.toFixed(_POINT_COORDINATES_PRECISION_));
                })[this.point.index] +
                "<br>" +
                "<b>" +
                yAxisName +
                ": </b>  " +
                this.y.toFixed(_POINT_COORDINATES_PRECISION_)
            );
        };
    }

    yAxis() {
        return {
            ...super.yAxis(),
            gridZIndex: 1,
            plotLines: this.fermiEnergy
                ? this.plotSingleLine({
                      value: 0.0,
                      width: 2, // to be shown above above grid/tickLine at zero
                      label: {
                          text: "E_F",
                          style: {
                              color: "red",
                          },
                          y: -5,
                          x: -10,
                      },
                  })
                : [],
        };
    }

    get overrideConfig() {
        const { xDataArray } = this;
        return {
            chart: {
                animation: false,
                type: "spline",
                zoomType: "xy",
            },
            plotOptions: {
                spline: {
                    lineWidth: 2,
                    states: {
                        hover: {
                            lineWidth: 6,
                        },
                    },
                    marker: {
                        enabled: false,
                    },
                },
            },
            tooltip: {
                valueSuffix: "",
                formatter: this.tooltipFormatter(xDataArray),
            },
            legend: {
                enabled: false,
            },
        };
    }
}

type Schema = BandStructurePropertySchema;

type Base = typeof Property<Schema> & Constructor<BandStructurePropertySchemaMixin>;

export default class BandStructureProperty extends (Property as Base) implements Schema {
    readonly subtitle: string = "Electronic Bandstructure";

    readonly yAxisTitle: string = `Energy (${this.yAxis.units})`;

    readonly chartConfig: Options;

    static readonly isRefined = true;

    static readonly propertyName = PropertyName.band_structure;

    static readonly propertyType = PropertyType.non_scalar;

    constructor(
        config: Omit<Schema, "name"> & {
            fermiEnergy?: number | null;
            pointsPath?: KPointPath;
        },
    ) {
        super({ ...config, name: BandStructureProperty.propertyName });
        this.chartConfig = new BandStructureConfig(this, {
            fermiEnergy: config.fermiEnergy,
            pointsPath: config.pointsPath,
        }).config;
    }
}

bandStructurePropertySchemaMixin(BandStructureProperty.prototype);
