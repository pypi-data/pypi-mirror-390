/* eslint-disable no-unused-expressions */
import type { BandStructurePropertySchema } from "@mat3ra/esse/dist/js/types";
import type { KPointPath } from "@mat3ra/made/dist/js/lattice/reciprocal/lattice_reciprocal";
import { expect } from "chai";

import BandStructureProperty from "../../../src/js/properties/non-scalar/BandStructureProperty";
import { PropertyType } from "../../../src/js/settings";

describe("BandStructureProperty", () => {
    const config: Omit<BandStructurePropertySchema, "name"> = {
        xAxis: {
            label: "kpoints",
            units: "crystal",
        },
        yAxis: {
            label: "energy",
            units: "eV",
        },
        spin: [0.5, -0.5],
        xDataArray: [
            [0, 0.1, 0.2, 0.3, 0.4, 0.5],
            [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        ],
        yDataSeries: [
            [-5.0, -4.0, -3.0, -2.0, -1.0, 0.0] as [number, ...number[]],
            [0.0, 1.0, 2.0, 3.0, 4.0, 5.0] as [number, ...number[]],
        ],
    };

    const mockPointsPath: KPointPath = [
        { point: "Γ", steps: 10, coordinates: [0, 0, 0] },
        { point: "X", steps: 10, coordinates: [0.5, 0, 0] },
    ];

    it("should create a band structure property with correct constructor, propertyType, propertyName, and defined properties", () => {
        const bandStructureProperty = new BandStructureProperty(config);

        // Test basic properties
        expect(bandStructureProperty).to.be.instanceOf(BandStructureProperty);
        expect(BandStructureProperty.propertyType).equal(PropertyType.non_scalar);
        expect(BandStructureProperty.propertyName).equal("band_structure");
        expect(BandStructureProperty.isRefined).to.be.true;

        // Test defined properties
        expect(bandStructureProperty.subtitle).to.equal("Electronic Bandstructure");
        expect(bandStructureProperty.yAxisTitle).to.equal("Energy (eV)");
        expect(bandStructureProperty.chartConfig).to.exist;
        expect(bandStructureProperty.chartConfig).to.be.an("object");
    });

    it("should accept additional constructor options", () => {
        // Test with fermiEnergy
        const propertyWithFermi = new BandStructureProperty({
            ...config,
            fermiEnergy: 0.5,
        });

        // Test with pointsPath
        const propertyWithPath = new BandStructureProperty({
            ...config,
            pointsPath: mockPointsPath,
        });

        // Test with both options
        const propertyWithBoth = new BandStructureProperty({
            ...config,
            fermiEnergy: 0.5,
            pointsPath: mockPointsPath,
        });
        expect(propertyWithBoth).to.be.instanceOf(BandStructureProperty);
        expect(propertyWithPath).to.be.instanceOf(BandStructureProperty);
        expect(propertyWithFermi).to.be.instanceOf(BandStructureProperty);
    });
});
