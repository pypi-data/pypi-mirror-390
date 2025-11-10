import type { FermiEnergyPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import FermiEnergyProperty from "../../../src/js/properties/scalar/FermiEnergyProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("FermiEnergyProperty", () => {
    it("should create a fermi energy property with correct constructor, propertyType, and propertyName", () => {
        const config: Omit<FermiEnergyPropertySchema, "name"> = {
            value: 5.2,
            units: "eV",
        };

        const fermiEnergyProperty = new FermiEnergyProperty(config);

        expect(fermiEnergyProperty).to.be.instanceOf(FermiEnergyProperty);
        expect(FermiEnergyProperty.propertyType).equal(PropertyType.scalar);
        expect(FermiEnergyProperty.propertyName).equal(PropertyName.fermi_energy);
    });
});
