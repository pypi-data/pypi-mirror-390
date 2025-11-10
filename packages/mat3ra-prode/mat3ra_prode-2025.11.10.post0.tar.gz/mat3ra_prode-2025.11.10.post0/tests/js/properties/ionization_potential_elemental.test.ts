import type { IonizationPotentialElementalPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import IonizationPotentialElementalProperty from "../../../src/js/properties/scalar/IonizationPotentialElementalProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("IonizationPotentialElementalProperty", () => {
    it("should create an ionization potential elemental property with correct constructor, propertyType, and propertyName", () => {
        const config: Omit<IonizationPotentialElementalPropertySchema, "name"> = {
            value: 13.6,
            units: "eV",
        };

        const ionizationPotentialProperty = new IonizationPotentialElementalProperty(config);

        expect(ionizationPotentialProperty).to.be.instanceOf(IonizationPotentialElementalProperty);
        expect(IonizationPotentialElementalProperty.propertyType).equal(PropertyType.scalar);
        expect(IonizationPotentialElementalProperty.propertyName).equal(
            PropertyName.ionization_potential,
        );
    });
});
