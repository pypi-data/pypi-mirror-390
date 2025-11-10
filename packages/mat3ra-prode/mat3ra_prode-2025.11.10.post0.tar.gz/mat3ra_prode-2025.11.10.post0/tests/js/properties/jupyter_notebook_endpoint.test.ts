import type { JupyterNotebookEndpointPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import JupyterNotebookEndpointProperty from "../../../src/js/properties/non-scalar/JupyterNotebookEndpointProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("JupyterNotebookEndpointProperty", () => {
    it("should create a jupyter notebook endpoint property with correct constructor, propertyType, and propertyName", () => {
        const config: Omit<JupyterNotebookEndpointPropertySchema, "name"> = {
            host: "localhost",
            port: 8888,
            token: "abc123def456",
        };

        const jupyterNotebookEndpointProperty = new JupyterNotebookEndpointProperty(config);

        expect(jupyterNotebookEndpointProperty).to.be.instanceOf(JupyterNotebookEndpointProperty);
        expect(JupyterNotebookEndpointProperty.propertyType).equal(PropertyType.non_scalar);
        expect(JupyterNotebookEndpointProperty.propertyName).equal(
            PropertyName.jupyter_notebook_endpoint,
        );
    });
});
