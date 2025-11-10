import type { StressTensorPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import StressTensorProperty from "../../../src/js/properties/tensor/StressTensorProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("StressTensorProperty", () => {
    it("should create a stress tensor property with correct constructor, propertyType, and propertyName", () => {
        const config: Omit<StressTensorPropertySchema, "name"> = {
            units: "kbar",
            value: [
                [1.2, 0.3, -0.1],
                [0.3, 0.8, 0.2],
                [-0.1, 0.2, 1.5],
            ],
        };

        const stressTensorProperty = new StressTensorProperty(config);

        expect(stressTensorProperty).to.be.instanceOf(StressTensorProperty);
        expect(StressTensorProperty.propertyType).equal(PropertyType.tensor);
        expect(StressTensorProperty.propertyName).equal(PropertyName.stress_tensor);
    });
});
