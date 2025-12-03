# Agent Flows Deep Dive

## Overview

Agent flows in AnythingLLM are **complex multi-step automations that work as skills**. They are registered as callable functions in the AIbitat framework (just like regular skills), but internally execute a **sequence of blocks/steps** with **persistent state through flow variables**.

---

## 1. Agent Flows as Skills

### 1.1 How Flows Work as Skills

Agent flows are **NOT** different from regular skills in terms of registration:

```
Flow Definition → Flow Plugin Object → aibitat.use() → aibitat.function() → functions Map
```

**Key difference:** Instead of executing inline code (like a regular skill), flows execute a series of sequential blocks.

### 1.2 Flow Registration

**Location:** `server/utils/agentFlows/index.js`

When flows are discovered and registered:

```javascript
// AgentFlows.loadFlowPlugin(uuid) returns a plugin object
{
  name: `flow_${uuid}`,
  description: `Execute agent flow: ${flow.name}`,
  plugin: (_runtimeArgs = {}) => ({
    name: `flow_${uuid}`,
    description: flow.config.description || `Execute agent flow: ${flow.name}`,
    setup: (aibitat) => {
      aibitat.function({
        name: `flow_${uuid}`,
        description: flow.config.description || `Execute agent flow: ${flow.name}`,
        parameters: {
          type: "object",
          properties: variables.reduce((acc, v) => {
            if (v.name) {
              acc[v.name] = {
                type: "string",
                description: v.description || `Value for variable ${v.name}`,
              };
            }
            return acc;
          }, {}),
        },
        handler: async (args) => {
          // Handler calls AgentFlows.executeFlow()
          const result = await AgentFlows.executeFlow(uuid, args, aibitat);
          
          // If directOutput, skip further LLM processing
          if (result.directOutput) {
            aibitat.skipHandleExecution = true;
            return AgentFlows.stringifyResult(result.directOutput);
          }
          
          return AgentFlows.stringifyResult(result);
        },
      });
    },
  }),
  flowName: flow.name,
}
```

**The flow's handler is the entry point:** When the LLM decides to call the flow, it invokes `AgentFlows.executeFlow()`.

---

## 2. Flow Definition Structure

### 2.1 Flow Storage

**Location:** `server/storage/plugins/agent-flows/`

```
server/storage/plugins/agent-flows/
└── {flow-uuid}.json
```

### 2.2 Flow Configuration Format

```json
{
  "name": "Data Processing Workflow",
  "description": "Fetch data from API, process with LLM, return results",
  "active": true,
  "steps": [
    {
      "type": "start",
      "config": {
        "variables": [
          {
            "name": "apiUrl",
            "value": "https://api.example.com/data",
            "description": "The API endpoint URL"
          },
          {
            "name": "userId",
            "value": "",
            "description": "User ID to fetch data for"
          }
        ]
      }
    },
    {
      "type": "apiCall",
      "config": {
        "url": "${apiUrl}?userId=${userId}",
        "method": "GET",
        "headers": [
          {
            "key": "Authorization",
            "value": "Bearer token123"
          }
        ],
        "responseVariable": "apiResponse"
      }
    },
    {
      "type": "llmInstruction",
      "config": {
        "instruction": "Analyze this data and summarize the key insights: ${apiResponse}",
        "resultVariable": "analysis"
      }
    },
    {
      "type": "webScraping",
      "config": {
        "url": "${apiResponse.relatedUrl}",
        "resultVariable": "scrapedContent"
      }
    }
  ]
}
```

---

## 3. Block Types

### 3.1 START Block

**Purpose:** Initialize flow variables with default values.

**Configuration:**
```javascript
{
  type: "start",
  config: {
    variables: [
      {
        name: "variableName",
        value: "defaultValue",
        description: "Optional description"
      },
      // ... more variables
    ]
  }
}
```

**Role:**
- Defines all variables that can be passed to the flow
- Sets default values (can be overridden by LLM arguments)
- All variables become properties of the flow function's JSON Schema
- The LLM can pass custom values as arguments

**Example:**
```json
{
  "type": "start",
  "config": {
    "variables": [
      { "name": "searchQuery", "value": "", "description": "What to search for" },
      { "name": "maxResults", "value": "10", "description": "Maximum results to return" }
    ]
  }
}
```

When registered as a skill, the flow's parameters become:
```javascript
parameters: {
  type: "object",
  properties: {
    searchQuery: { type: "string", description: "What to search for" },
    maxResults: { type: "string", description: "Maximum results to return" }
  }
}
```

### 3.2 API_CALL Block

**Purpose:** Make HTTP requests to external APIs.

**Configuration:**
```javascript
{
  type: "apiCall",
  config: {
    url: "https://api.example.com/endpoint",           // Can use ${variables}
    method: "GET",                                     // GET, POST, PUT, PATCH, DELETE
    headers: [                                         // Optional
      { key: "Authorization", value: "Bearer token" },
      { key: "Content-Type", value: "application/json" }
    ],
    bodyType: "json",                                  // "json", "form", or "text"
    body: "{\"data\": \"value\"}",                      // For POST/PUT/PATCH, can use ${variables}
    formData: [                                        // Alternative to body for forms
      { key: "field1", value: "${variable1}" }
    ],
    responseVariable: "apiResult",                     // Store response in this variable
    directOutput: false                                // If true, return immediately (no further blocks)
  }
}
```

**Variable Substitution:**
```javascript
// Before execution:
url: "https://api.example.com/users?id=${userId}&limit=${pageSize}"

// After variable replacement (if userId="123", pageSize="50"):
url: "https://api.example.com/users?id=123&limit=50"
```

**Response Storage:**
```javascript
// After API call, response stored in variables:
this.variables["apiResult"] = { /* API response */ }

// Available to next blocks via ${apiResult}
```

### 3.3 LLM_INSTRUCTION Block

**Purpose:** Process data using the LLM with custom instructions.

**Configuration:**
```javascript
{
  type: "llmInstruction",
  config: {
    instruction: "Analyze this text and extract key points: ${apiResponse}",  // Can use ${variables}
    resultVariable: "processedResult"                   // Store LLM response
  }
}
```

**Execution:**
```javascript
// The instruction string (with variables replaced) becomes the user message
const provider = aibitat.getProviderForConfig(aibitat.defaultProvider);
const completion = await provider.complete([
  {
    role: "user",
    content: instruction  // e.g., "Analyze this text and extract key points: {...}"
  }
]);

// Result stored in variables
this.variables["processedResult"] = completion.result;
```

### 3.4 WEB_SCRAPING Block

**Purpose:** Extract content from web pages.

**Configuration:**
```javascript
{
  type: "webScraping",
  config: {
    url: "https://example.com/page",                   // Can use ${variables}
    resultVariable: "scrapedData",                     // Store scraped content
    directOutput: false                                // If true, return immediately
  }
}
```

---

## 4. Flow Variables: Definition, Passing, and Access

### 4.1 Variable Definition

Variables are defined in the START block:

```javascript
// In START block config:
{
  variables: [
    {
      name: "userId",
      value: "default123",
      description: "The user ID to fetch"
    },
    {
      name: "apiKey",
      value: "",
      description: "API authentication key"
    }
  ]
}
```

### 4.2 Variable Initialization

**Location:** `FlowExecutor.executeFlow()` in `server/utils/agentFlows/executor.js`

```javascript
async executeFlow(flow, initialVariables = {}, aibitat) {
  // Merge default variables from START block with passed-in variables
  this.variables = {
    // Extract from START block and reduce to { name: value } pairs
    ...flow.config.steps
      .find((s) => s.type === "start")
      ?.config?.variables.reduce(
        (acc, v) => ({ ...acc, [v.name]: v.value }), 
        {}
      ),
    // Override with variables passed from LLM
    ...initialVariables,  // ⭐ LLM-provided arguments
  };

  this.aibitat = aibitat;
  // ... execute all steps
}
```

**Example:**
```javascript
// START block variables:
{
  name: "userId",
  value: "user_default_123"
},
{
  name: "maxResults",
  value: "10"
}

// LLM calls flow with arguments:
{
  userId: "user_custom_456",
  // maxResults not provided, uses default "10"
}

// Final variables object:
{
  userId: "user_custom_456",      // ← Overridden by LLM
  maxResults: "10"                // ← From START block default
}
```

### 4.3 Variable Substitution Pattern

**Location:** `FlowExecutor.replaceVariables()` and `FlowExecutor.getValueFromPath()`

Variables are substituted using **`${variable.path}` syntax**:

```javascript
// Simple variable
"${userId}"  →  "user_custom_456"

// Nested object path
"${apiResponse.data.user.name}"  →  "John Doe"

// Array index with dot notation
"${results[0].id}"  →  "result_123"

// Complex path
"${apiResponse.data.items[2].metadata.createdAt}"  →  "2024-10-27"
```

**Implementation:**
```javascript
replaceVariables(config) {
  const deepReplace = (obj) => {
    if (typeof obj === "string") {
      // Replace all ${varName} patterns
      return obj.replace(/\${([^}]+)}/g, (match, varName) => {
        // Use dot notation to access nested values
        const value = this.getValueFromPath(this.variables, varName);
        return value !== undefined ? value : match;  // Return original if not found
      });
    }

    if (Array.isArray(obj)) return obj.map((item) => deepReplace(item));

    if (obj && typeof obj === "object") {
      const result = {};
      for (const [key, value] of Object.entries(obj)) {
        result[key] = deepReplace(value);
      }
      return result;
    }
    return obj;
  };

  return deepReplace(config);
}

// Nested path resolution
getValueFromPath(obj = {}, path = "") {
  // Handles: "data.items[0].name" → extracts nested value
  // Returns: "item_name" or undefined if path invalid
}
```

### 4.4 Variable Passing Between Blocks

Variables persist throughout flow execution and are passed to subsequent blocks:

**Execution Flow:**
```
Step 1: START block
  Variables: { userId: "123", apiKey: "abc" }

Step 2: API_CALL block
  Config BEFORE variable replacement:
    url: "https://api.example.com/user/${userId}"
    responseVariable: "apiResponse"
  
  Config AFTER variable replacement:
    url: "https://api.example.com/user/123"
  
  Execution:
    Result: { id: "123", name: "John", email: "john@example.com" }
  
  Variables AFTER step:
    { userId: "123", apiKey: "abc", apiResponse: {...} }
                                     ↑ New variable added

Step 3: LLM_INSTRUCTION block
  Config BEFORE variable replacement:
    instruction: "Summarize this user: ${apiResponse}"
  
  Config AFTER variable replacement:
    instruction: "Summarize this user: {\"id\":\"123\",\"name\":\"John\",\"email\":\"john@example.com\"}"
  
  Execution:
    Result: "John is a user with email john@example.com"
  
  Variables AFTER step:
    { userId: "123", apiKey: "abc", apiResponse: {...}, llmResult: "John is a user..." }
                                                         ↑ New variable added

Step 4: WEB_SCRAPING block
  Config BEFORE variable replacement:
    url: "${apiResponse.metadata.profile_url}"  // Uses result from Step 2
  
  Can access ANY previous variable
```

### 4.5 Variable Storage and Retrieval

```javascript
// During step execution
async executeStep(step) {
  // Step 1: Replace variables in config
  const config = this.replaceVariables(step.config);
  
  // Step 2: Execute step with replaced config
  let result;
  switch (step.type) {
    case "apiCall":
      result = await executeApiCall(config, context);
      break;
    // ... other cases
  }
  
  // Step 3: Store result in variables
  if (config.resultVariable || config.responseVariable) {
    const varName = config.resultVariable || config.responseVariable;
    this.variables[varName] = result;  // ⭐ Variable persists
  }
  
  return result;
}

// this.variables persists across all steps in a single flow execution
```

---

## 5. Sequential Block Execution

### 5.1 Execution Order

**Location:** `FlowExecutor.executeFlow()` in `server/utils/agentFlows/executor.js`

```javascript
async executeFlow(flow, initialVariables = {}, aibitat) {
  // ... initialize variables ...
  
  const results = [];
  let directOutputResult = null;

  // Execute blocks sequentially
  for (const step of flow.config.steps) {
    try {
      // Step 1: Execute current step
      const result = await this.executeStep(step);

      // Step 2: Check for directOutput flag
      if (result?.directOutput) {
        directOutputResult = result.result;
        break;  // ⭐ Stop execution, return directly
      }

      results.push({ success: true, result });
      
    } catch (error) {
      results.push({ success: false, error: error.message });
      break;  // ⭐ Stop on error
    }
  }

  return {
    success: results.every((r) => r.success),
    results,
    variables: this.variables,  // ⭐ All accumulated variables
    directOutput: directOutputResult,
  };
}
```

### 5.2 Execution Characteristics

**Sequential:** Each block waits for the previous one to complete
```
[START] → [API_CALL] → [LLM_INSTRUCTION] → [WEB_SCRAPING] → [END]
   ↓          ↓              ↓                   ↓
 Init     Make API      Process with        Scrape web
vars      get data         LLM               page
```

**Stops on Error:**
```javascript
catch (error) {
  results.push({ success: false, error: error.message });
  break;  // ⭐ No further blocks execute
}
```

**Stops on Direct Output:**
```javascript
if (result?.directOutput) {
  directOutputResult = result.result;
  break;  // ⭐ Skip remaining blocks
}
```

---

## 6. Flow Execution Flow

### 6.1 Complete Execution Journey

```
1. LLM decides to call flow
   {
     "functionCall": {
       "name": "flow_12345-uuid",
       "arguments": {
         "userId": "custom_user_456",
         "filters": "active"
       }
     }
   }

2. AIbitat looks up flow in functions Map
   fn = this.functions.get("flow_12345-uuid")

3. AIbitat calls flow's handler
   result = fn.handler({
     userId: "custom_user_456",
     filters: "active"
   })

4. Flow handler calls AgentFlows.executeFlow()
   const result = await AgentFlows.executeFlow(
     "12345-uuid",
     args,        // { userId, filters }
     aibitat
   )

5. FlowExecutor initializes
   FlowExecutor.executeFlow(flow, args, aibitat) {
     this.variables = {
       // From START block defaults
       apiKey: "key123",
       timeout: "30",
       // Override with LLM args
       userId: "custom_user_456",
       filters: "active"
     }
   }

6. Execute blocks sequentially
   - Block 1 (START): Initialize variables
   - Block 2 (API_CALL): Replace ${userId}, ${apiKey} in URL, make request, store result
   - Block 3 (LLM_INSTRUCTION): Replace ${apiResponse} in instruction, process with LLM
   - Block 4 (WEB_SCRAPING): Replace ${apiResponse.url} in URL, scrape page

7. Return flow result
   {
     success: true,
     results: [
       { success: true, result: {...} },  // START block
       { success: true, result: {...} },  // API_CALL block
       { success: true, result: "Summary..." },  // LLM_INSTRUCTION block
       { success: true, result: "Scraped content..." }  // WEB_SCRAPING block
     ],
     variables: {
       apiKey: "key123",
       userId: "custom_user_456",
       filters: "active",
       apiResponse: {...},
       llmResult: "Summary...",
       scrapedContent: "Scraped content..."
     },
     directOutput: null
   }

8. Flow handler returns stringified result
   return AgentFlows.stringifyResult(result)

9. Result added to message history
   { role: "function", content: "Result from flow..." }

10. LLM receives result and can call more tools or return final response
```

### 6.2 Direct Output Flag

Some blocks can set `directOutput: true` to bypass LLM further processing:

```javascript
// In flow config
{
  type: "apiCall",
  config: {
    url: "...",
    responseVariable: "finalResult",
    directOutput: true  // ← Skip remaining blocks
  }
}

// During execution
if (result?.directOutput) {
  directOutputResult = result.result;  // { directOutput: true, result: {...} }
  break;  // Stop processing
}

// In flow handler
if (!!result.directOutput) {
  aibitat.skipHandleExecution = true;  // ← Tell AIbitat to return directly
  return AgentFlows.stringifyResult(result.directOutput);
}
```

---

## 7. Comparison: Skill vs Flow

| Aspect | Regular Skill | Agent Flow |
|--------|---------------|-----------|
| **Definition** | Single async function | Series of sequential blocks |
| **Code Location** | `server/utils/agents/aibitat/plugins/` or `storage/plugins/agent-skills/` | `storage/plugins/agent-flows/{uuid}.json` |
| **Storage** | JavaScript module | JSON file |
| **Execution** | Single handler function | Multiple blocks with state |
| **State Management** | Parameter-based | Flow variables persist across blocks |
| **Registration** | `aibitat.function()` directly | Flow plugin wraps it in `aibitat.function()` |
| **Parameters** | Fixed in code | Derived from START block variables |
| **Error Handling** | In handler try-catch | Stops at first error block |
| **Complex Logic** | Inline in handler | Across multiple blocks |

---

## 8. Flow Variables Technical Details

### 8.1 Variable Scoping

Variables are **flow-wide scoped**:
- Defined in START block
- Available to all subsequent blocks
- Persist through entire flow execution
- NOT accessible to other flows or skills

```javascript
// Flow A variables
{
  userId: "123",
  apiData: {...}
}

// Flow B variables (separate instance)
{
  searchQuery: "test",
  results: [...]
}

// Each flow has isolated variable scope
```

### 8.2 Variable Mutation

Variables can be:
1. **Initialized:** In START block
2. **Overridden:** By LLM call arguments
3. **Added:** By block results (responseVariable/resultVariable)
4. **Referenced:** In subsequent blocks via `${varName}`
5. **Nested Access:** Via dot notation and array indexing

```javascript
// Initial state (from START block and LLM args)
{ userId: "456", maxResults: "10" }

// After API_CALL block
{ userId: "456", maxResults: "10", apiResponse: {...} }

// After LLM_INSTRUCTION block
{ userId: "456", maxResults: "10", apiResponse: {...}, llmResult: "..." }

// Variables available to subsequent blocks
next block can use: ${userId}, ${maxResults}, ${apiResponse.key}, ${llmResult}
```

### 8.3 Path Resolution Examples

```javascript
// Variables state:
{
  user: {
    id: "123",
    profile: {
      email: "user@example.com",
      tags: ["admin", "moderator"]
    }
  },
  responses: [
    { status: "success", data: "result1" },
    { status: "pending", data: "result2" }
  ]
}

// Path examples:
${user}                          // → {"id":"123","profile":{...}}
${user.id}                       // → "123"
${user.profile.email}            // → "user@example.com"
${user.profile.tags[0]}          // → "admin"
${responses[0].data}             // → "result1"
${responses[1].status}           // → "pending"
```

---

## 9. Flow as a Skill: Complete Example

### 9.1 Flow Definition (JSON)

```json
{
  "name": "Search and Summarize",
  "description": "Search the web for information and provide a summary",
  "active": true,
  "steps": [
    {
      "type": "start",
      "config": {
        "variables": [
          {
            "name": "query",
            "value": "",
            "description": "Search query to look up"
          }
        ]
      }
    },
    {
      "type": "apiCall",
      "config": {
        "url": "https://api.search.example.com/search?q=${query}",
        "method": "GET",
        "responseVariable": "searchResults"
      }
    },
    {
      "type": "webScraping",
      "config": {
        "url": "${searchResults.topResult.url}",
        "resultVariable": "pageContent"
      }
    },
    {
      "type": "llmInstruction",
      "config": {
        "instruction": "Summarize the following content in 3 bullet points: ${pageContent}",
        "resultVariable": "summary"
      }
    }
  ]
}
```

### 9.2 How It Functions as a Skill

**Discovery:**
```javascript
// AgentFlows.activeFlowPlugins() returns:
["@@flow_abc123-uuid"]
```

**Loading:**
```javascript
// AgentFlows.loadFlowPlugin("abc123-uuid") returns:
{
  name: "flow_abc123-uuid",
  description: "Search and Summarize",
  plugin: () => ({
    setup(aibitat) {
      aibitat.function({
        name: "flow_abc123-uuid",
        description: "Search and Summarize",
        parameters: {
          type: "object",
          properties: {
            query: {
              type: "string",
              description: "Search query to look up"
            }
          }
        },
        handler: async (args) => {
          const result = await AgentFlows.executeFlow("abc123-uuid", args, aibitat);
          if (result.directOutput) {
            aibitat.skipHandleExecution = true;
            return AgentFlows.stringifyResult(result.directOutput);
          }
          return AgentFlows.stringifyResult(result);
        }
      });
    }
  })
}
```

**LLM Invocation:**
```
LLM sees in available tools:
{
  "type": "function",
  "function": {
    "name": "flow_abc123-uuid",
    "description": "Search and Summarize",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "Search query to look up"
        }
      }
    }
  }
}
```

**LLM Calls Flow:**
```javascript
{
  "functionCall": {
    "name": "flow_abc123-uuid",
    "arguments": {
      "query": "artificial intelligence benefits"
    }
  }
}
```

**Execution:**
```
Variables initialized:
{
  query: "artificial intelligence benefits"
}

Block 1 - START:
  Initializes variables

Block 2 - API_CALL:
  Replace: url = "https://api.search.example.com/search?q=artificial intelligence benefits"
  Result: searchResults = { topResult: { url: "https://example.com/ai-benefits" }, ... }
  Variables: { query: "...", searchResults: {...} }

Block 3 - WEB_SCRAPING:
  Replace: url = "https://example.com/ai-benefits"
  Result: pageContent = "Artificial Intelligence has many benefits including..."
  Variables: { query: "...", searchResults: {...}, pageContent: "..." }

Block 4 - LLM_INSTRUCTION:
  Replace: instruction = "Summarize the following content in 3 bullet points: Artificial Intelligence has many benefits..."
  Result: summary = "• AI improves efficiency\n• AI enables automation\n• AI reduces costs"
  Variables: { query: "...", searchResults: {...}, pageContent: "...", summary: "..." }

Final Result:
{
  success: true,
  results: [...],
  variables: {...},
  directOutput: null
}
```

---

## Summary: Flows as Skills

| Aspect | Implementation |
|--------|-----------------|
| **Registration** | Like any skill: plugin → aibitat.use() → aibitat.function() |
| **Discovery** | AgentFlows.activeFlowPlugins() returns `@@flow_{uuid}` identifiers |
| **Parameters** | Derived from START block variables, become function parameters |
| **Handler** | Wraps FlowExecutor.executeFlow() |
| **State** | Flow variables persist across sequential blocks |
| **Variable Passing** | Via `${variable.path}` substitution pattern |
| **Error Handling** | Stops at first error, continues on success |
| **Direct Output** | Can bypass LLM further processing with directOutput flag |
| **Accessibility** | Available to LLM like any other skill |

---

## Files Reference

| File | Purpose |
|------|---------|
| `server/utils/agentFlows/index.js` | AgentFlows class - load, save, execute flows |
| `server/utils/agentFlows/executor.js` | FlowExecutor - sequential execution engine |
| `server/utils/agentFlows/flowTypes.js` | Block type definitions (START, API_CALL, LLM_INSTRUCTION, WEB_SCRAPING) |
| `server/utils/agentFlows/executors/api-call.js` | API_CALL block executor |
| `server/utils/agentFlows/executors/llm-instruction.js` | LLM_INSTRUCTION block executor |
| `server/utils/agentFlows/executors/web-scraping.js` | WEB_SCRAPING block executor |
| `server/storage/plugins/agent-flows/{uuid}.json` | Flow definitions storage |

