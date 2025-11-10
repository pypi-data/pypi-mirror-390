/* eslint-disable no-unused-expressions */
import type { PressurePropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import PressureProperty from "../../../src/js/properties/scalar/PressureProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("PressureProperty", () => {
    it("should create a pressure property with correct constructor, propertyType, propertyName, and isRefined", () => {
        const config: Omit<PressurePropertySchema, "name"> = {
            value: 1.0,
            units: "kbar",
        };

        const pressureProperty = new PressureProperty(config);

        expect(pressureProperty).to.be.instanceOf(PressureProperty);
        expect(PressureProperty.propertyType).equal(PropertyType.scalar);
        expect(PressureProperty.propertyName).equal(PropertyName.pressure);
        expect(PressureProperty.isRefined).to.be.true;
    });
});
