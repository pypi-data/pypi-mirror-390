import type { FinalStructurePropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import FinalStructureProperty from "../../../src/js/properties/non-scalar/FinalStructureProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("FinalStructureProperty", () => {
    it("should create a final structure property with correct constructor, propertyType, and propertyName", () => {
        const config: Omit<FinalStructurePropertySchema, "name"> = {
            isRelaxed: true,
            materialId: "12345",
        };

        const finalStructureProperty = new FinalStructureProperty(config);

        expect(finalStructureProperty).to.be.instanceOf(FinalStructureProperty);
        expect(FinalStructureProperty.propertyType).equal(PropertyType.non_scalar);
        expect(FinalStructureProperty.propertyName).equal(PropertyName.final_structure);
    });
});
