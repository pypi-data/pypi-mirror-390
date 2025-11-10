import type { DielectricTensorPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import DielectricTensorProperty from "../../../src/js/properties/non-scalar/DielectricTensorProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("DielectricTensorProperty", () => {
    it("should create a dielectric tensor property with correct constructor, propertyType, propertyName, and defined properties", () => {
        const config: Omit<DielectricTensorPropertySchema, "name"> = {
            values: [
                {
                    part: "real" as const,
                    spin: 0.5,
                    frequencies: [0, 1, 2, 3, 4, 5],
                    components: [
                        [1.0, 0.0, 0.0] as [number, number, number],
                        [0.0, 1.0, 0.0] as [number, number, number],
                        [0.0, 0.0, 1.0] as [number, number, number],
                        [1.1, 0.1, 0.0] as [number, number, number],
                        [0.1, 1.1, 0.0] as [number, number, number],
                        [0.0, 0.0, 1.1] as [number, number, number],
                    ],
                },
                {
                    part: "imaginary" as const,
                    spin: 0.5,
                    frequencies: [0, 1, 2, 3, 4, 5],
                    components: [
                        [0.1, 0.0, 0.0] as [number, number, number],
                        [0.0, 0.1, 0.0] as [number, number, number],
                        [0.0, 0.0, 0.1] as [number, number, number],
                        [0.2, 0.0, 0.0] as [number, number, number],
                        [0.0, 0.2, 0.0] as [number, number, number],
                        [0.0, 0.0, 0.2] as [number, number, number],
                    ],
                },
            ],
        };

        const dielectricTensorProperty = new DielectricTensorProperty(config);

        expect(dielectricTensorProperty).to.be.instanceOf(DielectricTensorProperty);
        expect(DielectricTensorProperty.propertyType).equal(PropertyType.non_scalar);
        expect(DielectricTensorProperty.propertyName).equal(PropertyName.dielectric_tensor);

        expect(dielectricTensorProperty.subtitle).to.equal("Dielectric Tensor");
        expect(dielectricTensorProperty.yAxisTitle).to.equal("Dielectric Tensor Component");
        expect(dielectricTensorProperty.xAxisTitle).to.equal("Frequency (eV)");
        expect(dielectricTensorProperty.chartConfig).to.be.an("array");
        expect(dielectricTensorProperty.chartConfig).to.have.length.greaterThan(0);
    });
});
