/* eslint-disable class-methods-use-this */
// eslint-disable-next-line max-classes-per-file
import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { PhononDensityOfStatesPropertySchema } from "@mat3ra/esse/dist/js/types";
import type { Options } from "highcharts";

import { type FormatterScope } from "../../charts/highcharts";
import {
    PhononDOSPropertySchemaMixin,
    phononDOSPropertySchemaMixin,
} from "../../generated/PhononDOSPropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";
import { DensityOfStatesConfig } from "./DensityOfStatesProperty";

type Schema = PhononDensityOfStatesPropertySchema;

class PhononDOSConfig extends DensityOfStatesConfig {
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
}

type Base = typeof Property<Schema> & Constructor<PhononDOSPropertySchemaMixin>;

export default class PhononDOSProperty extends (Property as Base) implements Schema {
    readonly chartConfig: Options;

    readonly subtitle: string = "Phonon Density Of States";

    readonly yAxisTitle: string = `Density Of States (${this.yAxis.units})`;

    readonly xAxisTitle: string = `Frequency (${this.xAxis.units})`;

    static readonly propertyName = PropertyName.phonon_dos;

    static readonly propertyType = PropertyType.non_scalar;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: PhononDOSProperty.propertyName });
        this.chartConfig = new PhononDOSConfig(this).config;
    }
}

phononDOSPropertySchemaMixin(PhononDOSProperty.prototype);
