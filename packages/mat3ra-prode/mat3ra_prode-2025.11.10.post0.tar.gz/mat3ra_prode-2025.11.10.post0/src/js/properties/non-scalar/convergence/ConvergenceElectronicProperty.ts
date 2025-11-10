import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { ConvergenceElectronicPropertySchema } from "@mat3ra/esse/dist/js/types";
import type { AxisLabelFormatterOptions, IndividualSeriesOptions, Options } from "highcharts";

import { type FormatterScope, HighChartsConfig } from "../../../charts/highcharts";
import {
    ConvergenceElectronicPropertySchemaMixin,
    convergenceElectronicPropertySchemaMixin,
} from "../../../generated/ConvergenceElectronicPropertySchemaMixin";
import Property from "../../../Property";
import { PropertyName, PropertyType } from "../../../settings";

type Schema = ConvergenceElectronicPropertySchema;

class ConvergenceElectronicConfig extends HighChartsConfig {
    constructor(monitor: ConvergenceElectronicProperty) {
        let iteration = 1;

        const series: IndividualSeriesOptions[] = monitor.data.map((values, index) => {
            const name = parseInt(index.toString(), 10) + 1;
            return {
                name: `step-${name}`,
                data: values.map((value) => {
                    // give points unique xAxis value to show multiple series properly in highCharts
                    const point: [number, number] = [iteration, Math.abs(value)];
                    iteration += 1;
                    return point;
                }),
            };
        });

        super({
            subtitle: "Convergence Electronic",
            yAxisTitle: `Convergence Electronic (${monitor.units})`,
            xAxisTitle: "Iterations",
            yAxisType: "logarithmic",
            series,
            legend: series.length > 1,
        });
    }

    // eslint-disable-next-line class-methods-use-this
    tooltipFormatter() {
        // note 'this' below refers to Highcharts tooltip scope
        // eslint-disable-next-line func-names
        return function (this: FormatterScope) {
            return "<b>iteration:</b> " + this.key + "<br><b>Δ E:</b> " + this.y.toExponential(1);
        };
    }

    yAxis() {
        return {
            ...super.yAxis(),
            labels: {
                formatter(this: AxisLabelFormatterOptions) {
                    return this.value.toExponential();
                },
            },
        };
    }
}

type Base = typeof Property<Schema> & Constructor<ConvergenceElectronicPropertySchemaMixin>;

class ConvergenceElectronicProperty extends (Property as Base) implements Schema {
    static readonly propertyName = PropertyName.convergence_electronic;

    static readonly propertyType = PropertyType.non_scalar;

    static readonly isConvergence = true;

    readonly chartConfig: Options;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: ConvergenceElectronicProperty.propertyName });
        this.chartConfig = new ConvergenceElectronicConfig(this).config;
    }
}

convergenceElectronicPropertySchemaMixin(ConvergenceElectronicProperty.prototype);

export default ConvergenceElectronicProperty;
