/* eslint-disable no-unused-expressions */
import type { FileContentPropertySchema } from "@mat3ra/esse/dist/js/types";
import { expect } from "chai";

import FileContentProperty from "../../../src/js/properties/non-scalar/FileContentProperty";
import { PropertyName, PropertyType } from "../../../src/js/settings";

describe("FileContentProperty", () => {
    it("should create a file content property with correct constructor, propertyType, and propertyName", () => {
        const config: Omit<FileContentPropertySchema, "name"> = {
            filetype: "text",
            objectData: {
                CONTAINER: "materials-data",
                NAME: "output.txt",
                PROVIDER: "aws",
                REGION: "us-east-1",
                SIZE: 1024,
                TIMESTAMP: "2023-12-01T10:30:00Z",
            },
            pathname: "/results/calculation_123",
            basename: "output.txt",
        };

        const fileContentProperty = new FileContentProperty(config);

        expect(fileContentProperty).to.be.instanceOf(FileContentProperty);
        expect(FileContentProperty.propertyType).equal(PropertyType.non_scalar);
        expect(FileContentProperty.propertyName).equal(PropertyName.file_content);
        expect(FileContentProperty.isAbleToReturnMultipleResults).to.be.true;
    });
});
