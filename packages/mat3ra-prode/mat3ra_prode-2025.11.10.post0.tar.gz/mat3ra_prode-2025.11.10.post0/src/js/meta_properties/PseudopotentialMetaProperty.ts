import type { Constructor } from "@mat3ra/code/dist/js/utils/types";
import type { FileDataItem as Schema } from "@mat3ra/esse/dist/js/types";
import uniqBy from "lodash/uniqBy";

import {
    type PseudopotentialMetaPropertySchemaMixin,
    pseudopotentialMetaPropertySchemaMixin,
} from "../generated/PseudopotentialMetaPropertySchemaMixin";
import MetaProperty from "../MetaProperty";
import { PropertyName, PropertyType } from "../settings";

type RawDataObject = {
    path: string;
};

enum CompatibleExchangeCorrelationKey {
    hse06 = "hse06",
}

type Base = typeof MetaProperty & Constructor<PseudopotentialMetaPropertySchemaMixin>;

export default class PseudopotentialMetaProperty extends (MetaProperty as Base) implements Schema {
    static readonly propertyName = PropertyName.pseudopotential;

    static readonly propertyType = PropertyType.non_scalar;

    static readonly compatibleExchangeCorrelation = {
        hse06: ["pbe", "hse06"],
    };

    declare _json: Omit<Schema, "name">;

    declare toJSON: () => Omit<Schema, "name">;

    constructor(config: Omit<Schema, "name">) {
        super({ ...config, name: PseudopotentialMetaProperty.propertyName });
    }

    get isCustom() {
        return this.source === "user";
    }

    /**
     * @summary Attempts filtering raw data by search text, split by "," into multiple regular expressions,
     *           splitting to multiple regexps allows to control the order of filtered items
     *           if raw data is not empty but filtered data is, returns first element of raw data (assumed to be default)
     * @note Filters by path!
     */
    static safelyFilterRawDataBySearchText(
        rawData: PseudopotentialMetaProperty[],
        searchText: string,
        separator = ",",
    ) {
        if (!searchText) return rawData;
        const filteredData: PseudopotentialMetaProperty[] = [];
        searchText.split(separator).forEach((txt) => {
            const text = txt.trim(); // remove whitespace and do nothing if empty string
            if (!text) return;
            try {
                const regexp = new RegExp(text);
                const filteredData_ = rawData.filter((el) => el.path.match(regexp));
                filteredData.push(...filteredData_);
            } catch (e: unknown) {
                if (e instanceof Error) {
                    console.error(e.message);
                }
            }
        });
        return filteredData.length ? filteredData : rawData.splice(0, 1);
    }

    static isCompatibleWithOther(
        functional: string,
    ): functional is CompatibleExchangeCorrelationKey {
        return Object.keys(this.compatibleExchangeCorrelation).includes(functional);
    }

    /**
     * @summary Exclusive filter of raw data by all fields of the passed object
     */
    static filterRawDataByExchangeCorrelation(
        rawData: PseudopotentialMetaProperty[],
        exchangeCorrelation: {
            functional: string;
            approximation: string;
        },
    ) {
        const { functional } = exchangeCorrelation;

        return rawData.filter((item) => {
            return this.isCompatibleWithOther(functional)
                ? this.compatibleExchangeCorrelation[functional].includes(
                      item.exchangeCorrelation?.functional || "",
                  )
                : functional === item.exchangeCorrelation?.functional;
        });
    }

    // filter unique (assuming that path is always unique)
    static filterUnique(array: PseudopotentialMetaProperty[]) {
        return uniqBy(array, (item) => item.path);
    }

    // filter unique by apps (assuming that path is always unique)
    static filterUniqueByAppName(array: PseudopotentialMetaProperty[], appName: string) {
        return PseudopotentialMetaProperty.filterUnique(this.filterByAppName(array, appName));
    }

    static filterRawDataByPath(rawData: RawDataObject[], pseudoPath = "") {
        const regexp = new RegExp(pseudoPath);
        return rawData.filter((el) => el.path.match(regexp));
    }

    static filterByAppName(pseudos: PseudopotentialMetaProperty[], appName: string) {
        return pseudos.filter((pseudo) => pseudo.apps.includes(appName));
    }

    static filterByElements(pseudos: PseudopotentialMetaProperty[], elements: string[]) {
        return pseudos.filter((pseudo) => elements.includes(pseudo.element));
    }

    /** Apply several filters at once.
     * @example
     * // filter object
     * {
     *     exchangeCorrelation: {
     *         approximation: "gga",
     *         functional: "pbe"
     *     },
     *     searchText: "gbrv",
     *     appName: "vasp",
     *     elements: ["Si", "Ne", "Fe"],
     * }
     */
    static applyPseudoFilters(
        pseudos: PseudopotentialMetaProperty[],
        pseudoFilter: {
            searchText?: string;
            appName?: string;
            type?: string;
            exchangeCorrelation?: {
                functional: keyof typeof PseudopotentialMetaProperty.compatibleExchangeCorrelation;
                approximation: string;
            };
            elements?: string[];
        },
    ) {
        let filteredPseudos = [...pseudos];

        Object.entries(pseudoFilter).forEach(([fKey, fValue]) => {
            if (typeof fValue === "string") {
                if (fKey === "searchText") {
                    filteredPseudos = this.safelyFilterRawDataBySearchText(filteredPseudos, fValue);
                } else if (fKey === "appName") {
                    filteredPseudos = this.filterByAppName(filteredPseudos, fValue);
                } else if (fKey === "type") {
                    filteredPseudos = this.filterByType(filteredPseudos, fValue);
                }
            } else if (
                typeof fValue === "object" &&
                "functional" in fValue &&
                "approximation" in fValue
            ) {
                filteredPseudos = this.filterRawDataByExchangeCorrelation(filteredPseudos, fValue);
            } else if (Array.isArray(fValue)) {
                filteredPseudos = this.filterByElements(filteredPseudos, fValue);
            } else {
                throw new Error(`Invalid filter value: ${fValue}`);
            }
        });

        return filteredPseudos;
    }

    /**
     * Sorts pseudos by the given pattern.
     * NOTE: This is currently used to prioritize gbrv pseudopotentials over norm-conserving ones for QE.
     */
    static sortPseudosByPattern(pseudos: PseudopotentialMetaProperty[], pattern = "/gbrv/") {
        return pseudos.concat([]).sort((a, b) => {
            return (b.path.includes(pattern) ? 1 : 0) - (a.path.includes(pattern) ? 1 : 0);
        });
    }

    /**
     * Prioritizes pseudos with 'default' and '5.2' (version) in path (VASP)
     */
    static sortByPathVASP(pseudos: PseudopotentialMetaProperty[], version = "5.2") {
        return pseudos.concat([]).sort((a, b) => {
            if (a.path.includes("default") && a.path.includes(version)) {
                return -1;
            }
            if (b.path.includes("default") && b.path.includes(version)) {
                return 1;
            }
            return 0;
        });
    }

    static filterByType(pseudos: PseudopotentialMetaProperty[], pseudoType?: string) {
        if (pseudoType === undefined || pseudoType === "any") return pseudos;
        return pseudos.filter((pseudo) => pseudo.type.includes(pseudoType));
    }
}

pseudopotentialMetaPropertySchemaMixin(PseudopotentialMetaProperty.prototype);
