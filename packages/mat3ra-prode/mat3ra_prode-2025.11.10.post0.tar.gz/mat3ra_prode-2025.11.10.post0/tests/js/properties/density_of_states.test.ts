/* eslint-disable no-unused-expressions */
import type { DensityOfStatesPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import DensityOfStatesProperty from "../../../src/js/properties/non-scalar/DensityOfStatesProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("DensityOfStatesProperty", () => {
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
        legend: [
            {
                element: "Total",
                electronicState: "DOS",
                spin: 0.5 as const,
            },
            {
                element: "s",
                electronicState: "DOS",
                spin: -0.5 as const,
            },
        ],
    };

    it("should create a density of states property with correct constructor, propertyType, propertyName, and defined properties", () => {
        const densityOfStatesProperty = new DensityOfStatesProperty(config);

        // Test basic properties
        expect(densityOfStatesProperty).to.be.instanceOf(DensityOfStatesProperty);
        expect(DensityOfStatesProperty.propertyType).equal(PropertyType.non_scalar);
        expect(DensityOfStatesProperty.propertyName).equal(PropertyName.density_of_states);
        expect(DensityOfStatesProperty.isRefined).to.be.true;

        // Test defined properties
        expect(densityOfStatesProperty.subtitle).to.equal("Density Of States");
        expect(densityOfStatesProperty.yAxisTitle).to.equal("Density Of States (states/unitcell)");
        expect(densityOfStatesProperty.xAxisTitle).to.equal("Energy (eV)");
        expect(densityOfStatesProperty.chartConfig).to.exist;
        expect(densityOfStatesProperty.chartConfig).to.be.an("object");
    });

    it("should accept additional constructor options", () => {
        // Test with fermiEnergy
        const propertyWithFermi = new DensityOfStatesProperty({
            ...config,
            fermiEnergy: 2.5,
        });
        expect(propertyWithFermi).to.be.instanceOf(DensityOfStatesProperty);

        // Test with null fermiEnergy
        const propertyWithNullFermi = new DensityOfStatesProperty({
            ...config,
            fermiEnergy: null,
        });
        expect(propertyWithNullFermi).to.be.instanceOf(DensityOfStatesProperty);

        // Test without fermiEnergy
        const propertyWithoutFermi = new DensityOfStatesProperty(config);
        expect(propertyWithoutFermi).to.be.instanceOf(DensityOfStatesProperty);
    });
});
