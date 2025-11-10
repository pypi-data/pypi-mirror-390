/* eslint-disable no-unused-expressions */
import type { IsRelaxedPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import IsRelaxedProperty from "../../../src/js/properties/non-scalar/IsRelaxedProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("IsRelaxedProperty", () => {
    it("should create an is relaxed property with correct constructor, propertyType, propertyName, and isRefined", () => {
        const config: Omit<IsRelaxedPropertySchema, "name"> = {
            value: true,
            materialId: "12345",
        };

        const isRelaxedProperty = new IsRelaxedProperty(config);

        expect(isRelaxedProperty).to.be.instanceOf(IsRelaxedProperty);
        expect(IsRelaxedProperty.propertyType).equal(PropertyType.non_scalar);
        expect(IsRelaxedProperty.propertyName).equal(PropertyName.is_relaxed);
        expect(IsRelaxedProperty.isRefined).to.be.true;
    });
});
