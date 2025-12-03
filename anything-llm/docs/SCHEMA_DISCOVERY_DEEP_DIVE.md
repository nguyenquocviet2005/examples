# How Agents Discover Input/Output Schemas of Skills

## Quick Answer

Agents discover skill schemas through a **function registry** that gets passed to the LLM. When the agent needs to execute a skill:

1. **Schema Discovery** - AIbitat gathers all active skills' function definitions
2. **Schema Validation** - JSON Schema validates function parameters
3. **Schema Sending** - Schemas sent to LLM as "tools" or "functions"
4. **LLM Decision** - LLM sees available tools and their schemas
5. **Function Calling** - LLM calls function with proper parameters
6. **Handler Execution** - Handler validates and executes
7. **Result Return** - Result passed back to LLM

---

## Architecture: Function Discovery Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Chat Request                       │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│         WORKSPACE_AGENT.getDefinition() Called              │
│    Gathers all skill definitions from multiple sources      │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
        ┌──────────────┴──────────────┐
        ↓                             ↓
   DEFAULT_SKILLS          CONFIGURABLE_SKILLS
   (rag-memory)            (web-browsing)
   (doc-summarizer)        (sql-agent)
   (web-scraping)          (create-chart)
        │                       │
        └──────────────┬────────┘
                       ↓
   ┌─────────────────────────────────┐
   │   ImportedPlugin.activeImportedPlugins()
   │   (Load from storage/plugins/)
   └─────────────────────────────────┘
                       ↓
   ┌─────────────────────────────────┐
   │   AIBITAT FUNCTION REGISTRY
   │   Map<string, FunctionConfig>
   │
   │   {
   │     "rag-memory": FunctionConfig,
   │     "web-browsing": FunctionConfig,
   │     "sql-agent": FunctionConfig,
   │     "text-analyzer": FunctionConfig,
   │     ...
   │   }
   └─────────────────────────────────┘
                       ↓
   ┌─────────────────────────────────┐
   │   FORMAT SCHEMAS FOR LLM
   │   Convert to provider format:
   │   - OpenAI: tools/functions
   │   - Anthropic: tool_use format
   │   - Others: Custom format
   └─────────────────────────────────┘
                       ↓
   ┌─────────────────────────────────┐
   │   SEND TO LLM WITH MESSAGE
   │   {
   │     messages: [...],
   │     tools: [
   │       {
   │         name: "rag-memory",
   │         description: "...",
   │         parameters: { ... }
   │       },
   │       ...
   │     ]
   │   }
   └─────────────────────────────────┘
                       ↓
   ┌─────────────────────────────────┐
   │   LLM RESPONDS WITH FUNCTION CALL
   │   {
   │     type: "function_call",
   │     name: "rag-memory",
   │     arguments: {
   │       action: "search",
   │       content: "user query"
   │     }
   │   }
   └─────────────────────────────────┘
                       ↓
   ┌─────────────────────────────────┐
   │   LOOKUP FUNCTION IN REGISTRY
   │   const fn = this.functions.get("rag-memory")
   └─────────────────────────────────┘
                       ↓
   ┌─────────────────────────────────┐
   │   VALIDATE ARGUMENTS
   │   Check against JSON Schema
   │   parameters
   └─────────────────────────────────┘
                       ↓
   ┌─────────────────────────────────┐
   │   EXECUTE HANDLER
   │   const result = await fn.handler(args)
   └─────────────────────────────────┘
                       ↓
   ┌─────────────────────────────────┐
   │   RETURN RESULT TO LLM
   │   Add result to message history
   │   LLM can call more tools or respond
   └─────────────────────────────────┘
```

---

## Key Code: Function Registration

### Where Functions Get Registered

**File**: `server/utils/agents/aibitat/index.js`

```javascript
/**
 * Register a function in the AIbitat registry
 * This is called by each skill's setup() function
 */
function(functionConfig) {
  this.functions.set(functionConfig.name, functionConfig);
  return this;
}
```

### Function Configuration Structure

Each function registered contains this schema:

```javascript
{
  name: "skill-name",
  description: "What this skill does",
  
  // JSON Schema for input validation
  parameters: {
    $schema: "http://json-schema.org/draft-07/schema#",
    type: "object",
    properties: {
      param1: {
        type: "string",
        description: "Description of param1"
      },
      param2: {
        type: "number",
        enum: [1, 2, 3],
        description: "Choices for param2"
      }
    },
    additionalProperties: false
  },
  required: ["param1"],
  
  // Examples for LLM few-shot learning
  examples: [
    {
      prompt: "Example user request",
      call: JSON.stringify({ param1: "value" })
    }
  ],
  
  // The actual implementation
  handler: async function(params) {
    // Execute logic
    return result;
  }
}
```

---

## Step 1: Gathering Function Definitions

### Code Location
**File**: `server/utils/agents/defaults.js`

```javascript
async function agentSkillsFromSystemSettings() {
  const systemFunctions = [];

  // 1. Load DEFAULT_SKILLS (always present)
  const _disabledDefaultSkills = safeJsonParse(
    await SystemSettings.getValueOrFallback(
      { label: "disabled_agent_skills" },
      "[]"
    ),
    []
  );
  
  DEFAULT_SKILLS.forEach((skill) => {
    if (!_disabledDefaultSkills.includes(skill))
      systemFunctions.push(AgentPlugins[skill].name);
  });

  // 2. Load CONFIGURABLE_SKILLS from database
  const _setting = safeJsonParse(
    await SystemSettings.getValueOrFallback(
      { label: "default_agent_skills" },
      "[]"
    ),
    []
  );
  
  _setting.forEach((skillName) => {
    if (!AgentPlugins.hasOwnProperty(skillName)) return;
    
    // Handle multi-level plugins
    if (Array.isArray(AgentPlugins[skillName].plugin)) {
      for (const subPlugin of AgentPlugins[skillName].plugin) {
        systemFunctions.push(
          `${AgentPlugins[skillName].name}#${subPlugin.name}`
        );
      }
      return;
    }
    
    systemFunctions.push(AgentPlugins[skillName].name);
  });

  return systemFunctions;
}
```

### How Agent Gets Definition

**File**: `server/utils/agents/defaults.js`

```javascript
const WORKSPACE_AGENT = {
  name: "@agent",
  getDefinition: async (provider = null, workspace = null, user = null) => {
    return {
      role: await Provider.systemPrompt({ provider, workspace, user }),
      functions: [
        // 1. Default skills (from database settings)
        ...(await agentSkillsFromSystemSettings()),
        
        // 2. Imported/custom plugins (from storage)
        ...ImportedPlugin.activeImportedPlugins(),
        
        // 3. Agent flows
        ...AgentFlows.activeFlowPlugins(),
        
        // 4. MCP servers
        ...(await new MCPCompatibilityLayer().activeMCPServers()),
      ],
    };
  },
};
```

---

## Step 2: Building Function Objects

### In AIbitat's reply() Method

**File**: `server/utils/agents/aibitat/index.js` (line 576)

```javascript
async reply(route) {
  const fromConfig = this.getAgentConfig(route.from);
  const chatHistory = this.getOrFormatNodeChatHistory(route);
  
  const messages = [
    {
      content: fromConfig.role,
      role: "system",
    },
    ...chatHistory,
  ];

  // KEY PART: Get the function definitions
  const functions = fromConfig.functions
    ?.map((name) => this.functions.get(this.#parseFunctionName(name)))
    .filter((a) => !!a);

  // Pass functions to provider
  const provider = this.getProviderForConfig({
    ...this.defaultProvider,
    ...fromConfig,
  });

  let content;
  if (provider.supportsAgentStreaming) {
    content = await this.handleAsyncExecution(
      provider,
      messages,
      functions,  // <- Functions sent here
      route.from
    );
  } else {
    content = await this.handleExecution(
      provider,
      messages,
      functions,  // <- Functions sent here
      route.from
    );
  }

  this.newMessage({ ...route, content });
  return content;
}
```

**What `this.functions` contains**:
```javascript
this.functions = new Map<string, FunctionConfig>();

// After all skills are registered, it has:
{
  "rag-memory": { name, description, parameters, handler, examples },
  "web-browsing": { name, description, parameters, handler, examples },
  "document-summarizer": { name, description, parameters, handler, examples },
  "text-analyzer": { name, description, parameters, handler, examples },
  // ... more skills
}
```

---

## Step 3: Formatting for LLM Provider

### OpenAI Provider Example

**File**: `server/utils/agents/aibitat/providers/openai.js`

```javascript
#formatFunctions(functions) {
  return functions.map((func) => ({
    type: "function",
    name: func.name,
    description: func.description,
    parameters: func.parameters,  // <- JSON Schema sent to LLM
    strict: false,
  }));
}

async stream(messages, functions = [], eventHandler = null) {
  const response = await this.client.responses.create({
    model: this.model,
    input: this.#formatToResponsesInput(messages),
    stream: true,
    store: false,
    parallel_tool_calls: false,
    ...(Array.isArray(functions) && functions?.length > 0
      ? { tools: this.#formatFunctions(functions) }  // <- Formatted schemas
      : {}),
  });
  
  // ... handle streaming response
}
```

### What Gets Sent to OpenAI

```json
{
  "model": "gpt-4o",
  "messages": [...],
  "tools": [
    {
      "type": "function",
      "name": "rag-memory",
      "description": "Search local documents or store in memory",
      "parameters": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
          "action": {
            "type": "string",
            "enum": ["search", "store"],
            "description": "Search or store action"
          },
          "content": {
            "type": "string",
            "description": "Query or content to store"
          }
        },
        "additionalProperties": false
      }
    },
    {
      "type": "function",
      "name": "web-browsing",
      "description": "Search using search engine",
      "parameters": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "Search query"
          }
        },
        "additionalProperties": false
      }
    }
  ]
}
```

---

## Step 4: LLM Calls Function

LLM receives the tools and decides to use one:

```json
{
  "type": "function_call",
  "name": "rag-memory",
  "call_id": "call_abc123",
  "arguments": {
    "action": "search",
    "content": "What is AnythingLLM?"
  }
}
```

---

## Step 5: Handler Execution

### In handleAsyncExecution()

**File**: `server/utils/agents/aibitat/index.js` (line 670)

```javascript
if (completionStream.functionCall) {
  const { name, arguments: args } = completionStream.functionCall;
  
  // 1. Lookup function in registry
  const fn = this.functions.get(name);

  if (!fn) {
    // Function not found - ask LLM to try again
    return await this.handleAsyncExecution(
      provider,
      [
        ...messages,
        {
          name,
          role: "function",
          content: `Function "${name}" not found. Try again.`,
          originalFunctionCall: completionStream.functionCall,
        },
      ],
      functions,
      byAgent
    );
  }

  // 2. Execute the function handler
  fn.caller = byAgent || "agent";
  
  this?.introspect?.(
    `${fn.caller} is executing \`${name}\` tool ${JSON.stringify(args, null, 2)}`
  );

  // 3. Call the handler with validated arguments
  const result = await fn.handler(args);
  
  // 4. Return result to LLM
  return await this.handleAsyncExecution(
    provider,
    [
      ...messages,
      {
        name,
        role: "function",
        content: result,
        originalFunctionCall: completionStream.functionCall,
      },
    ],
    functions,
    byAgent
  );
}
```

---

## JSON Schema: Complete Reference

### Parameter Types

```javascript
parameters: {
  $schema: "http://json-schema.org/draft-07/schema#",
  type: "object",
  properties: {
    // String parameter
    text: {
      type: "string",
      description: "Text input"
    },
    
    // String with restricted choices
    action: {
      type: "string",
      enum: ["search", "store", "delete"],
      description: "Action to perform"
    },
    
    // Number parameter
    maxResults: {
      type: "number",
      description: "Max results",
      minimum: 1,
      maximum: 100
    },
    
    // Boolean parameter
    useCache: {
      type: "boolean",
      description: "Use cached results"
    },
    
    // Array parameter
    tags: {
      type: "array",
      items: { type: "string" },
      description: "List of tags"
    },
    
    // Object parameter
    filter: {
      type: "object",
      properties: {
        field: { type: "string" },
        value: { type: "string" }
      }
    }
  },
  additionalProperties: false  // Don't allow extra fields
}
```

### Required Parameters

```javascript
required: ["text", "action"]  // These must be provided
```

---

## Real Example: text-analyzer Skill

### Function Definition (Input Schema)

```javascript
aibitat.function({
  name: "text-analyzer",
  description: "Analyze text for keywords, sentiment, statistics, readability",
  
  parameters: {
    $schema: "http://json-schema.org/draft-07/schema#",
    type: "object",
    properties: {
      text: {
        type: "string",
        description: "Text content to analyze"
      },
      analysis_type: {
        type: "string",
        enum: ["keywords", "sentiment", "statistics", "readability"],
        description: "Type of analysis"
      }
    },
    additionalProperties: false
  },
  
  required: ["text", "analysis_type"],
  
  examples: [
    {
      prompt: "What keywords are in this text?",
      call: JSON.stringify({
        text: "the text from user",
        analysis_type: "keywords"
      })
    }
  ],
  
  // Handler gets called with validated parameters
  handler: async function({ text, analysis_type }) {
    // Return output schema
    return `**Analysis Result:** ...`;  // String output
  }
})
```

### What LLM Sees

```json
{
  "type": "function",
  "name": "text-analyzer",
  "description": "Analyze text for keywords, sentiment...",
  "parameters": {
    "type": "object",
    "properties": {
      "text": { "type": "string", "description": "Text content" },
      "analysis_type": { 
        "type": "string", 
        "enum": ["keywords", "sentiment", "statistics", "readability"]
      }
    },
    "required": ["text", "analysis_type"]
  }
}
```

### Output Schema (Implicit)

Output is determined by handler return value:
- Always a **string** for most skills
- Can be **formatted markdown** with headers, lists, etc.
- Can trigger **special output** via `_replySpecialAttributes`

---

## Provider Format Differences

### OpenAI
```javascript
tools: [
  {
    type: "function",
    name: "skill-name",
    description: "...",
    parameters: { /* JSON Schema */ }
  }
]
```

### Anthropic
```javascript
tools: [
  {
    name: "skill-name",
    description: "...",
    input_schema: { /* JSON Schema */ }
  }
]
```

### Generic OpenAI-compatible
```javascript
functions: [
  {
    name: "skill-name",
    description: "...",
    parameters: { /* JSON Schema */ }
  }
]
```

Each provider has a method like `#formatFunctions()` that converts the generic function config to provider-specific format.

---

## Function Discovery Sequence

```
1. Server starts
   ├─ AIbitat initialized
   ├─ Built-in skills loaded from plugins/
   └─ Skill setup() called for each
      └─ aibitat.function() called
         └─ Functions added to this.functions Map

2. User sends message with @agent
   ├─ getDefinition() called
   ├─ Gathers enabled skills from database
   ├─ Loads imported plugins from storage
   └─ Returns function name list

3. Agent reply() called
   ├─ Gets functions for this agent
   ├─ Looks up function configs in registry
   ├─ Provider formats schemas
   └─ Sends to LLM with message

4. LLM responds with function call
   ├─ Provider parses response
   ├─ Function looked up in registry
   ├─ Handler executed with parameters
   └─ Result sent back to LLM

5. LLM can call more functions or respond
```

---

## Key Takeaways

✅ **Schema Discovery**: Functions stored in `AIbitat.functions` Map during skill registration
✅ **Schema Format**: JSON Schema (draft-07) for parameter validation
✅ **Schema Sending**: Provider formats and sends to LLM with message
✅ **Schema Validation**: LLM must match required parameters to schema
✅ **Handler Lookup**: Function found in registry before execution
✅ **Input Validation**: Parameters validated against JSON Schema
✅ **Output**: Handler returns string (or special formatted output)

---

## Related Code

- **Skill Registration**: `server/utils/agents/aibitat/index.js` line 988
- **Function Gathering**: `server/utils/agents/defaults.js`
- **Reply/Execution**: `server/utils/agents/aibitat/index.js` lines 576-724
- **Provider Formatting**: `server/utils/agents/aibitat/providers/*.js`
- **OpenAI Specific**: `server/utils/agents/aibitat/providers/openai.js`
