import type { TotalForcesPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import TotalForcesProperty from "../../../src/js/properties/scalar/TotalForceProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("TotalForcesProperty", () => {
    it("should create a total force property with correct constructor, propertyType, and propertyName", () => {
        const config: Omit<TotalForcesPropertySchema, "name"> = {
            value: 1.0,
            units: "eV/bohr",
        };

        const totalForcesProperty = new TotalForcesProperty(config);

        expect(totalForcesProperty).to.be.instanceOf(TotalForcesProperty);
        expect(TotalForcesProperty.propertyType).equal(PropertyType.scalar);
        expect(TotalForcesProperty.propertyName).equal(PropertyName.total_force);
    });
});
