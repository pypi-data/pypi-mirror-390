/* eslint-disable no-unused-expressions */
import type { SurfaceEnergyPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import SurfaceEnergyProperty from "../../../src/js/properties/scalar/SurfaceEnergyProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("SurfaceEnergyProperty", () => {
    it("should create a surface energy property with correct constructor, propertyType, propertyName, and isRefined", () => {
        const config: Omit<SurfaceEnergyPropertySchema, "name"> = {
            value: 2.5,
            units: "eV/A^2",
        };

        const surfaceEnergyProperty = new SurfaceEnergyProperty(config);

        expect(surfaceEnergyProperty).to.be.instanceOf(SurfaceEnergyProperty);
        expect(SurfaceEnergyProperty.propertyType).equal(PropertyType.scalar);
        expect(SurfaceEnergyProperty.propertyName).equal(PropertyName.surface_energy);
        expect(SurfaceEnergyProperty.isRefined).to.be.true;
    });
});
