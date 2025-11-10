import type { AtomicForcesPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import AtomicForcesProperty from "../../../src/js/properties/tensor/AtomicForcesProperty";
import { PropertyType } from "../../../src/js/settings";

describe("AtomicForcesProperty", () => {
    it("should create an atomic forces property with correct constructor, propertyType, and propertyName", () => {
        const config: Omit<AtomicForcesPropertySchema, "name"> = {
            units: "eV/bohr",
            values: [
                {
                    value: [0.1, -0.2, 0.3],
                    id: 1,
                },
            ],
        };

        const atomicForcesProperty = new AtomicForcesProperty(config);

        expect(atomicForcesProperty).to.be.instanceOf(AtomicForcesProperty);
        expect(AtomicForcesProperty.propertyType).equal(PropertyType.tensor);
        expect(AtomicForcesProperty.propertyName).equal("atomic_forces");
    });
});
