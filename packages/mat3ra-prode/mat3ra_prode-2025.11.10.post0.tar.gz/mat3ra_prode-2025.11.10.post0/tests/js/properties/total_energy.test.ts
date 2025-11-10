/* eslint-disable no-unused-expressions */
import type { TotalEnergyPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import TotalEnergyProperty from "../../../src/js/properties/scalar/TotalEnergyProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("TotalEnergyProperty", () => {
    it("should create a total energy property with correct constructor, propertyType, propertyName, and isRefined", () => {
        const config: Omit<TotalEnergyPropertySchema, "name"> = {
            value: -1234.56,
            units: "eV",
        };

        const totalEnergyProperty = new TotalEnergyProperty(config);

        expect(totalEnergyProperty).to.be.instanceOf(TotalEnergyProperty);
        expect(TotalEnergyProperty.propertyType).equal(PropertyType.scalar);
        expect(TotalEnergyProperty.propertyName).equal(PropertyName.total_energy);
        expect(TotalEnergyProperty.isRefined).to.be.true;
    });
});
