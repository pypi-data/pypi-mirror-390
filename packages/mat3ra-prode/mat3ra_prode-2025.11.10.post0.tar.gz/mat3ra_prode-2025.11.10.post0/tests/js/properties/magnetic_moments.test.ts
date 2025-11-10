import type { MagneticMomentsPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import MagneticMomentsProperty from "../../../src/js/properties/tensor/MagneticMomentsProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("MagneticMomentsProperty", () => {
    it("should create a magnetic moments property with correct constructor, propertyType, and propertyName", () => {
        const config: Omit<MagneticMomentsPropertySchema, "name"> = {
            units: "uB",
            values: [
                {
                    value: [0.0, 0.0, 2.0],
                    id: 1,
                },
                {
                    value: [0.0, 0.0, -2.0],
                    id: 2,
                },
            ],
        };

        const magneticMomentsProperty = new MagneticMomentsProperty(config);

        expect(magneticMomentsProperty).to.be.instanceOf(MagneticMomentsProperty);
        expect(MagneticMomentsProperty.propertyType).equal(PropertyType.tensor);
        expect(MagneticMomentsProperty.propertyName).equal(PropertyName.magnetic_moments);
    });
});
