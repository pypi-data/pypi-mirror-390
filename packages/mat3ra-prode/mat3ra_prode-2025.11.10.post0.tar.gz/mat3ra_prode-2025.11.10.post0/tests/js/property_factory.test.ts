import { expect } from "chai";

import { PropertyFactory, PropertyName } from "../../src/js";

describe("PropertyFactory", () => {
    it("should return arrays of property names for different categories", () => {
        // Test all getter methods return arrays
        const refinedPropertyNames = PropertyFactory.getRefinedPropertyNames();
        const convergencePropertyNames = PropertyFactory.getConvergencePropertyNames();
        const multipleResultsPropertyNames = PropertyFactory.getMultipleResultsPropertyNames();
        const scalarPropertyNames = PropertyFactory.getScalarPropertyNames();
        const nonScalarPropertyNames = PropertyFactory.getNonScalarPropertyNames();

        // Verify all methods return arrays
        expect(refinedPropertyNames).to.be.an("array");
        expect(convergencePropertyNames).to.be.an("array");
        expect(multipleResultsPropertyNames).to.be.an("array");
        expect(scalarPropertyNames).to.be.an("array");
        expect(nonScalarPropertyNames).to.be.an("array");

        // Verify arrays are not empty
        expect(refinedPropertyNames.length).to.be.greaterThan(0);
        expect(convergencePropertyNames.length).to.be.greaterThan(0);
        expect(multipleResultsPropertyNames.length).to.be.greaterThan(0);
        expect(scalarPropertyNames.length).to.be.greaterThan(0);
        expect(nonScalarPropertyNames.length).to.be.greaterThan(0);

        // Verify all returned values are valid PropertyName enum values
        const allPropertyNames = [
            ...refinedPropertyNames,
            ...convergencePropertyNames,
            ...multipleResultsPropertyNames,
            ...scalarPropertyNames,
            ...nonScalarPropertyNames,
        ];

        allPropertyNames.forEach((propertyName) => {
            expect(Object.values(PropertyName)).to.include(propertyName);
        });
    });

    it("should return specific known properties in correct categories", () => {
        const refinedPropertyNames = PropertyFactory.getRefinedPropertyNames();
        const convergencePropertyNames = PropertyFactory.getConvergencePropertyNames();
        const multipleResultsPropertyNames = PropertyFactory.getMultipleResultsPropertyNames();
        const scalarPropertyNames = PropertyFactory.getScalarPropertyNames();
        const nonScalarPropertyNames = PropertyFactory.getNonScalarPropertyNames();

        // Test specific known properties are in correct categories
        expect(refinedPropertyNames).to.include(PropertyName.total_energy);
        expect(refinedPropertyNames).to.include(PropertyName.band_structure);
        expect(refinedPropertyNames).to.include(PropertyName.density_of_states);

        expect(convergencePropertyNames).to.include(PropertyName.convergence_electronic);
        expect(convergencePropertyNames).to.include(PropertyName.convergence_ionic);

        expect(multipleResultsPropertyNames).to.include(PropertyName.file_content);

        expect(scalarPropertyNames).to.include(PropertyName.total_energy);
        expect(scalarPropertyNames).to.include(PropertyName.fermi_energy);
        expect(scalarPropertyNames).to.include(PropertyName.pressure);

        expect(nonScalarPropertyNames).to.include(PropertyName.band_structure);
        expect(nonScalarPropertyNames).to.include(PropertyName.density_of_states);
        expect(nonScalarPropertyNames).to.include(PropertyName.file_content);
    });

    it("should not have overlapping categories", () => {
        const refinedPropertyNames = PropertyFactory.getRefinedPropertyNames();
        const convergencePropertyNames = PropertyFactory.getConvergencePropertyNames();
        const multipleResultsPropertyNames = PropertyFactory.getMultipleResultsPropertyNames();
        const scalarPropertyNames = PropertyFactory.getScalarPropertyNames();
        const nonScalarPropertyNames = PropertyFactory.getNonScalarPropertyNames();

        // Verify scalar and non-scalar properties don't overlap
        const scalarNonScalarOverlap = scalarPropertyNames.filter((name) =>
            nonScalarPropertyNames.includes(name),
        );
        expect(scalarNonScalarOverlap).to.have.length(0);

        // Verify convergence properties are not in refined properties
        const convergenceRefinedOverlap = convergencePropertyNames.filter((name) =>
            refinedPropertyNames.includes(name),
        );
        expect(convergenceRefinedOverlap).to.have.length(0);

        // Verify multiple results properties are not in scalar properties
        const multipleResultsScalarOverlap = multipleResultsPropertyNames.filter((name) =>
            scalarPropertyNames.includes(name),
        );
        expect(multipleResultsScalarOverlap).to.have.length(0);
    });
});
