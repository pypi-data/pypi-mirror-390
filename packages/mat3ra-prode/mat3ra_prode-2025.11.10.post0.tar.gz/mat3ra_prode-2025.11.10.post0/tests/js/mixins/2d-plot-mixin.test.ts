/* eslint-disable no-unused-expressions */
import type { DensityOfStatesPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import {
    type XDataArray,
    type YDataSeries,
    TwoDimensionalHighChartConfigMixin,
} from "../../../src/js/properties/include/mixins/2d_plot";
import DensityOfStatesProperty from "../../../src/js/properties/non-scalar/DensityOfStatesProperty";

describe("2D Plot Mixin Integration", () => {
    const config: Omit<DensityOfStatesPropertySchema, "name"> = {
        xAxis: {
            label: "energy",
            units: "eV",
        },
        yAxis: {
            label: "density of states",
            units: "states/unitcell",
        },
        xDataArray: [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5],
        yDataSeries: [
            [0.1, 0.2, 0.5, 1.0, 2.0, 3.0, 2.0, 1.0, 0.5, 0.2, 0.1] as [number, ...number[]],
            [0.05, 0.15, 0.4, 0.8, 1.5, 2.5, 1.5, 0.8, 0.4, 0.15, 0.05] as [number, ...number[]],
        ],
        legend: [],
    };

    it("should create a density of states property with 2D plot mixin integration", () => {
        const densityOfStatesProperty = new DensityOfStatesProperty(config);

        // Test basic property creation
        expect(densityOfStatesProperty).to.be.instanceOf(DensityOfStatesProperty);

        // Test 2D plot mixin getters
        expect(densityOfStatesProperty.xDataArray).to.exist;
        expect(densityOfStatesProperty.xDataArray).to.be.an("array");
        expect(densityOfStatesProperty.xDataArray).to.have.length(11);

        expect(densityOfStatesProperty.yDataSeries).to.exist;
        expect(densityOfStatesProperty.yDataSeries).to.be.an("array");
        expect(densityOfStatesProperty.yDataSeries).to.have.length(2);

        // Test chart configuration
        expect(densityOfStatesProperty.chartConfig).to.exist;
        expect(densityOfStatesProperty.chartConfig).to.be.an("object");
    });

    it("should test TwoDimensionalHighChartConfigMixin functionality", () => {
        const chartParams = {
            xDataArray: [1, 2, 3] as XDataArray,
            yDataSeries: [[10, 20, 30] as [number, ...number[]]] as YDataSeries,
            xAxis: { label: "x", units: "units" },
            yAxis: { label: "y", units: "units" },
            subtitle: "test",
            yAxisTitle: "y",
            xAxisTitle: "x",
        };

        const chartConfig = new TwoDimensionalHighChartConfigMixin(chartParams);

        // Test series generation
        expect(chartConfig.series).to.be.an("array");
        expect(chartConfig.series).to.have.length(1);
        expect(chartConfig.series[0].data).to.deep.equal([
            [1, 10],
            [2, 20],
            [3, 30],
        ]);

        // Test overrideConfig
        expect(chartConfig.overrideConfig).to.be.an("object");
    });
});
