#!/usr/bin/env node

/**
 * Script to generate mixin properties from JSON schema
 *
 * This script generates mixin functions for property/holder, property/meta_holder,
 * and property/proto_holder schemas automatically.
 *
 * Usage:
 *   npx ts-node scripts/generate-mixin-properties.ts
 */

import generateSchemaMixin from "@mat3ra/code/dist/js/generateSchemaMixin";
import allSchemas from "@mat3ra/esse/dist/js/schemas.json";
import type { JSONSchema7 } from "json-schema";

/**
 * Fields to skip during generation
 */
const SKIP_FIELDS = ["_id", "slug", "systemName", "schemaVersion"];

/**
 * Output file paths for each schema
 */
const OUTPUT_PATHS = {
    "property/holder": "src/js/generated/PropertyHolderSchemaMixin.ts",
    "property/meta-holder": "src/js/generated/MetaPropertyHolderSchemaMixin.ts",
    "property/proto-holder": "src/js/generated/ProtoPropertyHolderSchemaMixin.ts",
    "methods-directory/physical/psp/file-data-item":
        "src/js/generated/PseudopotentialMetaPropertySchemaMixin.ts",
    "properties-directory/non-scalar/average-potential-profile":
        "src/js/generated/AveragePotentialProfilePropertySchemaMixin.ts",
    "properties-directory/non-scalar/band-gaps": "src/js/generated/BandGapsPropertySchemaMixin.ts",
    "properties-directory/non-scalar/band-structure":
        "src/js/generated/BandStructurePropertySchemaMixin.ts",
    "properties-directory/non-scalar/charge-density-profile":
        "src/js/generated/ChargeDensityProfilePropertySchemaMixin.ts",
    "properties-directory/non-scalar/density-of-states":
        "src/js/generated/DensityOfStatesPropertySchemaMixin.ts",
    "properties-directory/non-scalar/dielectric-tensor":
        "src/js/generated/DielectricTensorPropertySchemaMixin.ts",
    "properties-directory/non-scalar/file-content":
        "src/js/generated/FileContentPropertySchemaMixin.ts",
    "properties-directory/non-scalar/final-structure":
        "src/js/generated/FinalStructurePropertySchemaMixin.ts",
    "properties-directory/non-scalar/hubbard-u": "src/js/generated/HubbardUPropertySchemaMixin.ts",
    "properties-directory/non-scalar/hubbard-v-nn":
        "src/js/generated/HubbardVNNPropertySchemaMixin.ts",
    "properties-directory/non-scalar/hubbard-v": "src/js/generated/HubbardVPropertySchemaMixin.ts",
    "properties-directory/non-scalar/is-relaxed":
        "src/js/generated/IsRelaxedPropertySchemaMixin.ts",
    "properties-directory/jupyter-notebook-endpoint":
        "src/js/generated/JupyterNotebookEndpointPropertySchemaMixin.ts",
    "properties-directory/non-scalar/phonon-dispersions":
        "src/js/generated/PhononDispersionsPropertySchemaMixin.ts",
    "properties-directory/non-scalar/phonon-dos":
        "src/js/generated/PhononDOSPropertySchemaMixin.ts",
    "properties-directory/non-scalar/potential-profile":
        "src/js/generated/PotentialProfilePropertySchemaMixin.ts",
    "properties-directory/non-scalar/reaction-energy-profile":
        "src/js/generated/ReactionEnergyProfilePropertySchemaMixin.ts",
    "properties-directory/workflow/convergence/ionic":
        "src/js/generated/ConvergenceIonicPropertySchemaMixin.ts",
    "properties-directory/workflow/convergence/electronic":
        "src/js/generated/ConvergenceElectronicPropertySchemaMixin.ts",
    "properties-directory/non-scalar/workflow": "src/js/generated/WorkflowPropertySchemaMixin.ts",
    "properties-directory/non-scalar/total-energy-contributions":
        "src/js/generated/TotalEnergyContributionsPropertySchemaMixin.ts",
    "properties-directory/scalar/fermi-energy":
        "src/js/generated/FermiEnergyPropertySchemaMixin.ts",
    "properties-directory/elemental/ionization-potential":
        "src/js/generated/IonizationPotentialElementalPropertySchemaMixin.ts",
    "properties-directory/scalar/pressure": "src/js/generated/PressurePropertySchemaMixin.ts",
    "properties-directory/scalar/reaction-energy-barrier":
        "src/js/generated/ReactionEnergyBarrierPropertySchemaMixin.ts",
    "properties-directory/scalar/surface-energy":
        "src/js/generated/SurfaceEnergyPropertySchemaMixin.ts",
    "properties-directory/scalar/total-energy":
        "src/js/generated/TotalEnergyPropertySchemaMixin.ts",
    "properties-directory/scalar/total-force": "src/js/generated/TotalForcePropertySchemaMixin.ts",
    "properties-directory/scalar/valence-band-offset":
        "src/js/generated/ValenceBandOffsetPropertySchemaMixin.ts",
    "properties-directory/scalar/zero-point-energy":
        "src/js/generated/ZeroPointEnergyPropertySchemaMixin.ts",
    "properties-directory/structural/atomic-forces":
        "src/js/generated/AtomicForcesPropertySchemaMixin.ts",
    "properties-directory/structural/magnetic-moments":
        "src/js/generated/MagneticMomentsPropertySchemaMixin.ts",
    "properties-directory/non-scalar/stress-tensor":
        "src/js/generated/StressTensorPropertySchemaMixin.ts",
    "properties-directory/structural/basis/atomic-constraints-property":
        "src/js/generated/AtomicConstraintsPropertySchemaMixin.ts",
    "properties-directory/structural/basis/boundary-conditions":
        "src/js/generated/BoundaryConditionsPropertySchemaMixin.ts",
};

function main() {
    // Type assertion to handle schema compatibility - the schemas from esse may have slightly different types
    const result = generateSchemaMixin(allSchemas as JSONSchema7[], OUTPUT_PATHS, SKIP_FIELDS);

    if (result.errorCount > 0) {
        process.exit(1);
    }
}

// Run the script if it's executed directly
main();
