/* eslint-disable no-unused-expressions */
import { expect } from "chai";

import Pseudopotential from "../../../src/js/meta_properties/PseudopotentialMetaProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("PseudopotentialMetaProperty", () => {
    const exchangeCorrelation = {
        functional: "pbe" as const,
        approximation: "gga" as const,
    };

    const pseudos = [
        new Pseudopotential({
            exchangeCorrelation,
            element: "Si",
            hash: "hash1",
            path: "/path/to/si/pbe/upf",
            apps: ["espresso"],
            source: "test",
            type: "nc" as const,
        }),
        new Pseudopotential({
            exchangeCorrelation,
            element: "C",
            hash: "hash2",
            path: "/path/to/c/gbrv/upf",
            apps: ["vasp"],
            source: "user",
            type: "paw" as const,
        }),
    ];

    it("should create a pseudopotential meta property with correct constructor, propertyType, propertyName, static properties, and custom getter", () => {
        expect(Pseudopotential.propertyType).equal(PropertyType.non_scalar);
        expect(Pseudopotential.propertyName).equal(PropertyName.pseudopotential);
        expect(Pseudopotential.compatibleExchangeCorrelation).to.be.an("object");
        expect(Pseudopotential.compatibleExchangeCorrelation).to.have.property("hse06");
        expect(Pseudopotential.compatibleExchangeCorrelation.hse06).to.be.an("array");

        expect(pseudos[0].isCustom).to.equal(false);
        expect(pseudos[1].isCustom).to.equal(true);
    });

    it("should test all static methods", () => {
        const filters = {
            searchText: "gbrv",
            appName: "vasp",
            type: "paw",
            elements: ["C"],
            exchangeCorrelation: {
                functional: "hse06" as const,
                approximation: "gga",
            },
        };

        const filteredResult = Pseudopotential.applyPseudoFilters(pseudos, filters);
        expect(filteredResult).to.have.length(1);
        expect(filteredResult[0].element).to.equal("C");
        expect(filteredResult[0].path).to.include("gbrv");
        expect(filteredResult[0].apps).to.include("vasp");
        expect(filteredResult[0].type).to.equal("paw");
        expect(filteredResult[0].exchangeCorrelation.functional).to.equal("pbe");
        expect(filteredResult[0].exchangeCorrelation.approximation).to.equal("gga");

        const invalidResult = Pseudopotential.applyPseudoFilters(pseudos, {
            searchText: "invalid[regex", // Invalid regex pattern
            elements: ["C"],
        });
        expect(invalidResult).to.have.length(0);

        const resultWithComma = Pseudopotential.applyPseudoFilters(pseudos, {
            searchText: "gbrv, ",
            elements: ["C"],
        });
        expect(resultWithComma).to.have.length(1);
        expect(resultWithComma[0].path).to.include("gbrv");

        // Test applyPseudoFilters with empty searchText
        const resultWithEmptySearch = Pseudopotential.applyPseudoFilters(pseudos, {
            searchText: "",
            elements: ["C"],
        });
        expect(resultWithEmptySearch).to.have.length(1);
        expect(resultWithEmptySearch[0].element).to.equal("C");

        const patternResult = Pseudopotential.sortPseudosByPattern(pseudos, "gbrv");
        expect(patternResult).to.have.length(2);
        expect(patternResult[0].path).to.include("gbrv");
        expect(patternResult[1].path).to.not.include("gbrv");

        const defaultResult = Pseudopotential.sortPseudosByPattern(pseudos);
        expect(defaultResult).to.have.length(2);
        expect(defaultResult[0].path).to.include("gbrv");

        // Test sortByPathVASP with different paths to cover all conditions
        const vaspPseudos = [
            new Pseudopotential({
                ...pseudos[0]._json,
                path: "/path/to/si/regular/upf",
            }),
            new Pseudopotential({
                ...pseudos[1]._json,
                path: "/path/to/c/default/5.2/upf",
            }),
            new Pseudopotential({
                ...pseudos[1]._json,
                path: "/path/to/o/default/5.1/upf",
            }),
        ];

        const vaspResult = Pseudopotential.sortByPathVASP(vaspPseudos);
        expect(vaspResult).to.have.length(3);
        expect(vaspResult).to.be.an("array");
        // The C pseudopotential with "default" and "5.2" should be first
        expect(vaspResult[0].path).to.include("default");
        expect(vaspResult[0].path).to.include("5.2");

        const rawData = pseudos.map((pseudo) => pseudo._json);
        const gbrvResults = Pseudopotential.filterRawDataByPath(rawData, "gbrv");
        expect(gbrvResults).to.have.length(1);
        expect(gbrvResults[0].path).to.include("gbrv");

        const uniqueByAppResults = Pseudopotential.filterUniqueByAppName(pseudos, "espresso");
        expect(uniqueByAppResults).to.have.length(1);
        expect(uniqueByAppResults[0].apps).to.include("espresso");

        expect(() => {
            // @ts-expect-error - invalid filter value
            Pseudopotential.applyPseudoFilters(pseudos, { invalidFilter: 123 });
        }).to.throw("Invalid filter value: 123");
    });
});
