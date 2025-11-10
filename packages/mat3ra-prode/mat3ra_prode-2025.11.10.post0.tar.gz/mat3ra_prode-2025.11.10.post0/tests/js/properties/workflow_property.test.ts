import type { WorkflowPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import WorkflowProperty from "../../../src/js/properties/non-scalar/WorkflowProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("WorkflowProperty", () => {
    it("should create a workflow property with correct constructor, propertyType, and propertyName", () => {
        const config: Omit<WorkflowPropertySchema, "name"> = {
            subworkflows: [
                {
                    units: [
                        {
                            type: "io",
                            subtype: "input",
                            source: "api",
                            input: [
                                {
                                    endpoint: "https://api.example.com/data",
                                    endpoint_options: {},
                                },
                            ],
                            flowchartId: "unit-1",
                        },
                    ],
                    model: {
                        type: "test_type",
                        subtype: "test_subtype",
                        method: {
                            type: "test_method_type",
                            subtype: "test_method_subtype",
                        },
                    },
                    application: {
                        shortName: "test_app",
                        summary: "Test application",
                        version: "1.0.0",
                    },
                    name: "test_subworkflow",
                },
            ],
            units: [
                {
                    type: "io",
                    subtype: "input",
                    source: "api",
                    input: [
                        {
                            endpoint: "https://api.example.com/data",
                            endpoint_options: {},
                        },
                    ],
                    flowchartId: "workflow-unit-1",
                },
            ],
        };

        const workflowProperty = new WorkflowProperty(config);

        expect(workflowProperty).to.be.instanceOf(WorkflowProperty);
        expect(WorkflowProperty.propertyType).equal(PropertyType.non_scalar);
        expect(WorkflowProperty.propertyName).equal(PropertyName.workflow_pyml_predict);
    });
});
