import type { ZeroPointEnergyPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import ZeroPointEnergyProperty from "../../../src/js/properties/scalar/ZeroPointEnergyProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("ZeroPointEnergyProperty", () => {
    it("should create a zero point energy property with correct constructor, propertyType, and propertyName", () => {
        const config: Omit<ZeroPointEnergyPropertySchema, "name"> = {
            value: 0.15,
            units: "eV",
        };

        const zeroPointEnergyProperty = new ZeroPointEnergyProperty(config);

        expect(zeroPointEnergyProperty).to.be.instanceOf(ZeroPointEnergyProperty);
        expect(ZeroPointEnergyProperty.propertyType).equal(PropertyType.scalar);
        expect(ZeroPointEnergyProperty.propertyName).equal(PropertyName.zero_point_energy);
    });
});
