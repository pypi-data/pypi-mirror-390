/* eslint-disable no-unused-expressions */
import type { AveragePotentialProfilePropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import AveragePotentialProfileProperty from "../../../src/js/properties/non-scalar/AveragePotentialProfileProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("AveragePotentialProfileProperty", () => {
    const config: Omit<AveragePotentialProfilePropertySchema, "name"> = {
        xDataArray: [
            [0, 0.1, 0.2, 0.3, 0.4, 0.5],
            [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        ],
        yDataSeries: [
            [0.1, 0.2, 0.3, 0.4, 0.5, 0.6] as [number, ...number[]],
            [0.2, 0.3, 0.4, 0.5, 0.6, 0.7] as [number, ...number[]],
        ],
        xAxis: {
            label: "z coordinate",
            units: "angstrom",
        },
        yAxis: {
            units: "eV",
            label: "energy" as const,
        },
    };

    it("should create an average potential profile property with correct constructor, propertyType, propertyName, and defined properties", () => {
        const averagePotentialProfileProperty = new AveragePotentialProfileProperty(config);

        // Test basic properties
        expect(averagePotentialProfileProperty).to.be.instanceOf(AveragePotentialProfileProperty);
        expect(AveragePotentialProfileProperty.propertyType).equal(PropertyType.non_scalar);
        expect(AveragePotentialProfileProperty.propertyName).equal(
            PropertyName.average_potential_profile,
        );
        expect(AveragePotentialProfileProperty.isRefined).to.be.true;

        // Test defined properties
        expect(averagePotentialProfileProperty.subtitle).to.equal("Average Potential Profile");
        expect(averagePotentialProfileProperty.yAxisTitle).to.equal("Energy (eV)");
        expect(averagePotentialProfileProperty.xAxisTitle).to.equal("Coordinate (angstrom)");
        expect(averagePotentialProfileProperty.chartConfig).to.exist;
        expect(averagePotentialProfileProperty.chartConfig).to.be.an("object");
    });
});
