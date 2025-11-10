/* eslint-disable no-unused-expressions */
import type { ReactionEnergyBarrierPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import ReactionEnergyBarrierProperty from "../../../src/js/properties/scalar/ReactionEnergyBarrierProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("ReactionEnergyBarrierProperty", () => {
    it("should create a reaction energy barrier property with correct constructor, propertyType, propertyName, and isRefined", () => {
        const config: Omit<ReactionEnergyBarrierPropertySchema, "name"> = {
            value: 25.5,
            units: "kJ/mol",
        };

        const reactionEnergyBarrierProperty = new ReactionEnergyBarrierProperty(config);

        expect(reactionEnergyBarrierProperty).to.be.instanceOf(ReactionEnergyBarrierProperty);
        expect(ReactionEnergyBarrierProperty.propertyType).equal(PropertyType.scalar);
        expect(ReactionEnergyBarrierProperty.propertyName).equal(
            PropertyName.reaction_energy_barrier,
        );
        expect(ReactionEnergyBarrierProperty.isRefined).to.be.true;
    });
});
