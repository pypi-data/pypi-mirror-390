/* eslint-disable no-unused-expressions */
import type { BandGapsPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import BandGapsProperty from "../../../src/js/properties/non-scalar/BandGapsProperty";
import { PropertyType } from "../../../src/js/settings";

describe("BandGapsProperty", () => {
    it("should create a band gaps property with correct constructor, propertyType, propertyName, and custom methods", () => {
        const config: Omit<BandGapsPropertySchema, "name"> = {
            values: [
                {
                    type: "direct" as const,
                    value: 1.5,
                    units: "eV" as const,
                },
                {
                    type: "indirect" as const,
                    value: 1.2,
                    units: "eV" as const,
                },
            ],
        };

        const bandGapsProperty = new BandGapsProperty(config);

        // Test basic properties
        expect(bandGapsProperty).to.be.instanceOf(BandGapsProperty);
        expect(BandGapsProperty.propertyType).equal(PropertyType.non_scalar);
        expect(BandGapsProperty.propertyName).equal("band_gaps");
        expect(BandGapsProperty.isRefined).to.be.true;

        // Test toRowValues method
        const rowValues = bandGapsProperty.toRowValues();
        expect(rowValues).to.be.an("array");
        expect(rowValues).to.have.length(2);

        const directRow = rowValues.find((row) => row.slug === "band_gaps:direct");
        const indirectRow = rowValues.find((row) => row.slug === "band_gaps:indirect");
        expect(directRow).to.exist;
        expect(indirectRow).to.exist;

        // Test flattenProperties method
        const flattened = bandGapsProperty.flattenProperties();
        expect(flattened).to.be.an("array");
        expect(flattened).to.have.length(2);
    });
});
