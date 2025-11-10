/* eslint-disable no-unused-expressions */
import type { ValenceBandOffsetPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import ValenceBandOffsetProperty from "../../../src/js/properties/scalar/ValenceBandOffsetProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("ValenceBandOffsetProperty", () => {
    it("should create a valence band offset property with correct constructor, propertyType, propertyName, and isRefined", () => {
        const config: Omit<ValenceBandOffsetPropertySchema, "name"> = {
            value: 0.5,
            units: "eV",
        };

        const valenceBandOffsetProperty = new ValenceBandOffsetProperty(config);

        expect(valenceBandOffsetProperty).to.be.instanceOf(ValenceBandOffsetProperty);
        expect(ValenceBandOffsetProperty.propertyType).equal(PropertyType.scalar);
        expect(ValenceBandOffsetProperty.propertyName).equal(PropertyName.valence_band_offset);
        expect(ValenceBandOffsetProperty.isRefined).to.be.true;
    });
});
