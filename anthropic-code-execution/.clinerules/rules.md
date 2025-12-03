# Agent Tool Discovery and Execution Rules

## Directory Structure Overview

Tools are organized hierarchically under the `servers/` directory:

```
servers/
├── google-drive/
│   ├── getDocument.ts
│   ├── createDocument.ts
│   ├── updateDocument.ts
│   ├── deleteDocument.ts
│   └── index.ts
├── salesforce/
│   ├── updateRecord.ts
│   ├── queryRecords.ts
│   ├── createRecord.ts
│   └── index.ts
└── [other-service]/
    ├── [tool-name].ts
    └── index.ts
```

## Rule 1: Tool Discovery Process

### When to Search for Tools
- The user requests an action that involves external services (Google Drive, Salesforce, etc.)
- The user mentions performing operations on data from third-party platforms
- The user asks about integration capabilities

### Discovery Steps
1. **Identify the Service**: Extract the target service from the user's request
   - Example: "Get a document from Google Drive" → Service = `google-drive`
   - Example: "Update a Salesforce record" → Service = `salesforce`

2. **Locate the Server Directory**: Find the corresponding folder under `servers/`
   ```
   servers/[service-name]/
   ```

3. **List Available Tools**: Scan the service directory for `.ts` files (excluding `index.ts`)
   - Each `.ts` file (except `index.ts`) represents one available tool
   - Tool names are derived from the filename (without `.ts` extension)
   - Use camelCase to understand the tool's purpose

4. **Match to User Request**: Map the user's action to the appropriate tool
   - User action: "create a new document" → Tool: `createDocument.ts`
   - User action: "query records" → Tool: `queryRecords.ts`
   - User action: "update data" → Tool: `updateRecord.ts` or `updateDocument.ts`

## Rule 2: Tool Execution Protocol

### Pre-Execution Checklist
- [ ] Service directory exists under `servers/`
- [ ] Required tool file exists (e.g., `servers/google-drive/getDocument.ts`)
- [ ] User has provided necessary parameters for the tool
- [ ] Tool purpose aligns with user's request

### Execution Steps
1. **Load Tool**: Reference the tool from its location
   ```
   servers/[service]/[tool-name].ts
   ```

2. **Prepare Parameters**: Extract and validate required parameters
   - Document ID, Record ID, Query filters, etc.
   - Check that all required fields are provided or requestable from the user

3. **Execute Tool**: Call the tool with the prepared parameters

4. **Handle Response**: Process the tool's output
   - Display results in a user-friendly format
   - Log any errors or exceptions
   - Suggest next steps if applicable

## Rule 3: Tool Naming Conventions

Tools follow predictable naming patterns that indicate their function:

| Pattern | Purpose | Example |
|---------|---------|---------|
| `get[Resource]` | Retrieve/read data | `getDocument`, `getRecords` |
| `create[Resource]` | Create new resource | `createDocument`, `createRecord` |
| `update[Resource]` | Modify existing resource | `updateRecord`, `updateDocument` |
| `delete[Resource]` | Remove resource | `deleteDocument`, `deleteRecord` |
| `query[Resources]` | Search/filter resources | `queryRecords`, `queryDocuments` |
| `list[Resources]` | Retrieve multiple items | `listDocuments`, `listRecords` |

## Rule 4: Common Service Examples

### Google Drive Service
Located at: `servers/google-drive/`

**Common Tools:**
- `getDocument.ts` - Fetch a document by ID
- `createDocument.ts` - Create a new document
- `updateDocument.ts` - Modify document content
- `deleteDocument.ts` - Remove a document
- `listDocuments.ts` - List all documents

**Typical Parameters:**
- `documentId` - The ID of the target document
- `title` - Document title (for create/update)
- `content` - Document body content

### Salesforce Service
Located at: `servers/salesforce/`

**Common Tools:**
- `queryRecords.ts` - Search for records
- `getRecords.ts` - Fetch specific records
- `createRecord.ts` - Add new record
- `updateRecord.ts` - Modify existing record
- `deleteRecord.ts` - Remove a record

**Typical Parameters:**
- `recordId` - The ID of the record
- `objectType` - Type of object (Account, Contact, Opportunity, etc.)
- `fields` - Field names and values to update

## Rule 5: Error Handling and Fallback

### If Tool Not Found
1. Verify the service name is spelled correctly
2. Check if the service directory exists in `servers/`
3. Suggest available services if service not found
4. Ask user if they meant a different service

### If Required Parameters Missing
1. Identify which parameters are required
2. Request the missing information from the user
3. Do not attempt to execute without required parameters

### If Execution Fails
1. Capture and display the error message
2. Suggest possible causes (authentication, invalid parameters, service down)
3. Ask user to verify parameters and retry

## Rule 6: Tool Index Integration

### Using index.ts
- Each service has an `index.ts` file that exports all available tools
- This file serves as the service's public API
- Tools should be imported and used through the `index.ts` export
- Example: `import * as googleDriveTools from 'servers/google-drive/index.ts'`

## Rule 7: Sequential Tool Execution

When a user task requires multiple tools:

1. **Plan the Sequence**: Determine the order of tool execution
   - Example: Create document → Get document → Update document
   - Example: Query records → Update records

2. **Execute in Order**: Run tools sequentially
   - Wait for each tool to complete before starting the next
   - Use output from previous tool as input for the next tool (if applicable)

3. **Aggregate Results**: Combine results from all tools for final response

## Rule 8: User Communication

### When Discovering Tools
- Inform user which service will be used
- List available tools if user request is ambiguous
- Confirm the correct tool before execution

### During Execution
- Show which tool is being executed
- Display any progress or intermediate results
- Provide clear status updates

### After Execution
- Show the final result clearly
- Explain what was accomplished
- Suggest related actions or follow-up steps
