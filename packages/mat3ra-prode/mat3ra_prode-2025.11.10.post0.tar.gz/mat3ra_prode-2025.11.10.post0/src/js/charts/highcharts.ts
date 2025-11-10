/* eslint-disable class-methods-use-this */

import type { AxisOptions, IndividualSeriesOptions, Options, PlotLines } from "highcharts";

import type { XDataArray } from "../properties/include/mixins/2d_plot";

/**
 * Callback JavaScript function to format the data label. Note that if a format is defined, the format takes
 * precedence and the formatter is ignored.
 * Available data are:
 * - this.percentage Stacked series and pies only. The point's percentage of the total.
 * - this.point      The point object. The point name, if defined, is available through this.point.name.
 * - this.series     The series object. The series name is available through this.series.name.
 * - this.total      Stacked series only. The total value at this point's x value.
 * - this.x:         The x value.
 * - this.y:         The y value.
 */
export type FormatterScope = {
    percentage: number;
    point: {
        name: string;
        index: number;
    };
    series: {
        name: string;
    };
    total: number;
    x: number;
    y: number;
    key: number;
};

export type Formatter = (this: FormatterScope) => string;

export interface HighChartsConfigParams {
    title?: string;
    subtitle: string;
    yAxisTitle?: string;
    xAxisTitle?: string;
    yAxisType: string;
    series?: IndividualSeriesOptions[];
    legend?: string[] | object[] | boolean;
}

/**
 * @description Base class for Highcharts configuration
 */
export abstract class HighChartsConfig implements HighChartsConfigParams {
    readonly title: HighChartsConfigParams["title"];

    readonly subtitle: HighChartsConfigParams["subtitle"];

    readonly yAxisTitle: HighChartsConfigParams["yAxisTitle"];

    readonly xAxisTitle: HighChartsConfigParams["xAxisTitle"];

    readonly yAxisType: HighChartsConfigParams["yAxisType"];

    readonly legend: HighChartsConfigParams["legend"];

    readonly _series: HighChartsConfigParams["series"];

    constructor({
        title,
        subtitle,
        yAxisTitle,
        xAxisTitle,
        yAxisType,
        series,
        legend,
    }: HighChartsConfigParams) {
        this.title = title;
        this.subtitle = subtitle;
        this.yAxisTitle = yAxisTitle;
        this.xAxisTitle = xAxisTitle;
        this.yAxisType = yAxisType;
        this._series = series;
        this.legend = legend;
    }

    yAxis(): AxisOptions {
        return {
            title: {
                text: this.yAxisTitle,
            },
            type: this.yAxisType,
            gridLineColor: "#eee",
            plotLines: [
                {
                    value: 0,
                    width: 1,
                    color: "#808080",
                },
            ],
        };
    }

    xAxis(): AxisOptions {
        return {
            title: {
                text: this.xAxisTitle,
            },
            tickPixelInterval: 200,
        };
    }

    // override in children
    abstract tooltipFormatter(_xDataArray?: XDataArray): (this: FormatterScope) => string;

    plotSingleLine({
        value,
        width = 1,
        label,
        color = "red",
        dashStyle = "dash",
    }: PlotLines): PlotLines[] {
        return [
            {
                value,
                width,
                label,
                color,
                dashStyle,
            },
        ];
    }

    get series() {
        return this._series;
    }

    get config(): Options {
        return {
            credits: {
                enabled: false,
            },
            chart: {
                animation: false,
                zoomType: "xy",
            },
            title: {
                text: "",
                x: -20, // center
            },
            subtitle: {
                text: this.subtitle,
                x: -20,
            },
            yAxis: this.yAxis(),
            xAxis: this.xAxis(),
            tooltip: {
                formatter: this.tooltipFormatter(),
            },
            plotOptions: {
                series: {
                    animation: false,
                },
            },
            legend: {
                enabled: Boolean(this.legend),
                maxHeight: 70,
            },
            series: this.series,
            ...this.overrideConfig,
        };
    }

    // use in child classes to add/override default config props
    get overrideConfig(): Options {
        return {};
    }
}
