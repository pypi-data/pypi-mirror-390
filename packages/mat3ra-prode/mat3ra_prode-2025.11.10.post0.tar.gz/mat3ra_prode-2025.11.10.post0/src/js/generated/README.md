# Generated Files

⚠️ **DO NOT MANUALLY EDIT FILES IN THIS DIRECTORY**

This directory contains auto-generated TypeScript files that are created by the build process. Any manual changes to these files will be overwritten the next time the generation script runs.

## How to regenerate these files

To regenerate all files in this directory, use the npm script:

```bash
npm run generate-mixins
```

## What these files are

These files contain schema mixins that are automatically generated based on the property definitions in the codebase. They provide type-safe schema definitions for various properties used throughout the application.

## If you need to modify the generated content

If you need to change the content of these files, you should:

1. Modify the schema definitions in the esse package that these mixins are based on
2. Update the generation script (`scripts/generate-mixins.ts`) if needed
3. Run `npm run generate-mixins` to regenerate the files

**Never edit these files directly!**
