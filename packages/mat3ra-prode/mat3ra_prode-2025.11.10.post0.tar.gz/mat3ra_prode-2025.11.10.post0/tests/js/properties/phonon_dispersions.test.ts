/* eslint-disable no-unused-expressions */
import type { PhononBandStructurePropertySchema } from "@mat3ra/esse/dist/js/types";
import type { KPointPath } from "@mat3ra/made/dist/js/lattice/reciprocal/lattice_reciprocal";
import { expect } from "chai";

import PhononDispersionsProperty from "../../../src/js/properties/non-scalar/PhononDispersionsProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("PhononDispersionsProperty", () => {
    const config: Omit<PhononBandStructurePropertySchema, "name"> = {
        xDataArray: [
            [0, 0.1, 0.2, 0.3, 0.4, 0.5],
            [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        ],
        yDataSeries: [
            [0.1, 0.2, 0.3, 0.4, 0.5, 0.6] as [number, ...number[]],
            [0.2, 0.3, 0.4, 0.5, 0.6, 0.7] as [number, ...number[]],
        ],
        xAxis: {
            label: "qpoints",
            units: "crystal",
        },
        yAxis: {
            units: "THz",
            label: "frequency" as const,
        },
    };

    const mockPointsPath: KPointPath = [
        { point: "Γ", steps: 10, coordinates: [0, 0, 0] },
        { point: "X", steps: 10, coordinates: [0.5, 0, 0] },
        { point: "M", steps: 10, coordinates: [0.5, 0.5, 0] },
        { point: "Γ", steps: 10, coordinates: [0, 0, 0] },
    ];

    it("should create a phonon dispersions property with correct constructor, propertyType, propertyName, and defined properties", () => {
        const phononDispersionsProperty = new PhononDispersionsProperty(config);

        // Test basic properties
        expect(phononDispersionsProperty).to.be.instanceOf(PhononDispersionsProperty);
        expect(PhononDispersionsProperty.propertyType).equal(PropertyType.non_scalar);
        expect(PhononDispersionsProperty.propertyName).equal(PropertyName.phonon_dispersions);

        // Test defined properties
        expect(phononDispersionsProperty.subtitle).to.equal("Phonon Dispersions");
        expect(phononDispersionsProperty.yAxisTitle).to.equal("Frequency (THz)");
        expect(phononDispersionsProperty.chartConfig).to.exist;
        expect(phononDispersionsProperty.chartConfig).to.be.an("object");
    });

    it("should accept additional constructor options", () => {
        // Test with pointsPath
        const propertyWithPath = new PhononDispersionsProperty({
            ...config,
            pointsPath: mockPointsPath,
        });
        expect(propertyWithPath).to.be.instanceOf(PhononDispersionsProperty);
        expect(propertyWithPath.chartConfig).to.exist;
    });
});
