import type { TotalEnergyContributionsPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import TotalEnergyContributionsProperty from "../../../src/js/properties/object/TotalEnergyContributionsProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("TotalEnergyContributionsProperty", () => {
    it("should create a total energy contributions property with correct constructor, propertyType, propertyName, and custom getter", () => {
        const config: Omit<TotalEnergyContributionsPropertySchema, "name"> = {
            units: "eV",
            hartree: {
                name: "hartree",
                value: -15.2,
            },
            exchange_correlation: {
                name: "exchange_correlation",
                value: -3.1,
            },
        };

        const totalEnergyContributionsProperty = new TotalEnergyContributionsProperty(config);

        expect(totalEnergyContributionsProperty).to.be.instanceOf(TotalEnergyContributionsProperty);
        expect(TotalEnergyContributionsProperty.propertyType).equal(PropertyType.object);
        expect(TotalEnergyContributionsProperty.propertyName).equal(
            PropertyName.total_energy_contributions,
        );
        expect(totalEnergyContributionsProperty.exchangeCorrelation).to.equal(
            totalEnergyContributionsProperty.exchange_correlation,
        );
    });
});
