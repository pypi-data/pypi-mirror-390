/* eslint-disable no-unused-expressions */
import type { ConvergenceElectronicPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import ConvergenceElectronicProperty from "../../../src/js/properties/non-scalar/convergence/ConvergenceElectronicProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("ConvergenceElectronicProperty", () => {
    it("should create a convergence electronic property with correct constructor, propertyType, propertyName, and defined properties", () => {
        const config: Omit<ConvergenceElectronicPropertySchema, "name"> = {
            data: [
                [1.0e-3, 5.0e-4, 2.0e-4, 1.0e-4, 5.0e-5],
                [2.0e-3, 1.0e-3, 5.0e-4, 2.0e-4, 1.0e-4],
            ],
            units: "eV",
        };

        const convergenceElectronicProperty = new ConvergenceElectronicProperty(config);

        // Test basic properties
        expect(convergenceElectronicProperty).to.be.instanceOf(ConvergenceElectronicProperty);
        expect(ConvergenceElectronicProperty.propertyType).equal(PropertyType.non_scalar);
        expect(ConvergenceElectronicProperty.propertyName).equal(
            PropertyName.convergence_electronic,
        );
        expect(ConvergenceElectronicProperty.isConvergence).to.be.true;

        // Test defined properties
        expect(convergenceElectronicProperty.chartConfig).to.exist;
        expect(convergenceElectronicProperty.chartConfig).to.be.an("object");
    });
});
