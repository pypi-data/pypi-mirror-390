/* eslint-disable class-methods-use-this */
/* eslint-disable max-classes-per-file */

import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { ReactionEnergyProfilePropertySchema } from "@mat3ra/esse/dist/js/types";
import type { Options } from "highcharts";

import {
    ReactionEnergyProfilePropertySchemaMixin,
    reactionEnergyProfilePropertySchemaMixin,
} from "../../generated/ReactionEnergyProfilePropertySchemaMixin";
import Property from "../../Property";
import { PropertyName, PropertyType } from "../../settings";
import { TwoDimensionalHighChartConfigMixin } from "../include/mixins/2d_plot";

type Schema = ReactionEnergyProfilePropertySchema;

export class ReactionEnergyProfileConfig extends TwoDimensionalHighChartConfigMixin {
    readonly tooltipXAxisName: string = "reaction coordinate";

    readonly tooltipYAxisName: string = "energy";
}

type Base = typeof Property<Schema> & Constructor<ReactionEnergyProfilePropertySchemaMixin>;

class ReactionEnergyProfileProperty extends (Property as Base) implements Schema {
    readonly subtitle: string = "Reaction Energy Profile";

    readonly yAxisTitle: string = `Energy (${this.yAxis.units})`;

    readonly xAxisTitle: string = "Reaction Coordinate";

    readonly chartConfig: Options = new ReactionEnergyProfileConfig(this).config;

    static readonly isRefined = true;

    static readonly propertyName = PropertyName.reaction_energy_profile;

    static readonly propertyType = PropertyType.non_scalar;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: ReactionEnergyProfileProperty.propertyName });
    }
}

reactionEnergyProfilePropertySchemaMixin(ReactionEnergyProfileProperty.prototype);

export default ReactionEnergyProfileProperty;
