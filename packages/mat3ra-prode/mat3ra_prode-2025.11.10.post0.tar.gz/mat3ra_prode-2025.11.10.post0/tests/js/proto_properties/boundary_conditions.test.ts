import type { BoundaryConditionsPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import BoundaryConditionsProperty from "../../../src/js/proto_properties/BoundaryConditionsProperty";
import { PropertyType } from "../../../src/js/settings";

describe("BoundaryConditionsProperty", () => {
    it("should create a boundary conditions property with correct constructor, propertyType, and propertyName", () => {
        const config: Omit<BoundaryConditionsPropertySchema, "name"> = {
            type: "pbc",
            offset: 0.0,
        };

        const boundaryConditionsProperty = new BoundaryConditionsProperty(config);

        expect(boundaryConditionsProperty).to.be.instanceOf(BoundaryConditionsProperty);
        expect(BoundaryConditionsProperty.propertyType).equal(PropertyType.non_scalar);
        expect(BoundaryConditionsProperty.propertyName).equal("boundary_conditions");
    });
});
