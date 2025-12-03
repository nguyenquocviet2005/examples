# Complete Skill Lifecycle in AnythingLLM's AIbitat Framework

## Table of Contents
1. [Skill Definition](#skill-definition)
2. [Skill Discovery](#skill-discovery)
3. [Skill Loading into Functions Map](#skill-loading)
4. [Functions Given to LLM](#functions-given-to-llm)
5. [LLM Response Execution](#llm-response-execution)

---

## 1. Skill Definition

### 1.1 Built-in Skills

Built-in skills are defined as JavaScript modules in `server/utils/agents/aibitat/plugins/`.

**Structure:**
```javascript
// server/utils/agents/aibitat/plugins/text-analyzer.js

const textAnalyzer = {
  name: "text-analyzer",              // Unique identifier
  startupConfig: {
    params: {},                        // Optional startup parameters
  },
  plugin: function () {
    return {
      name: this.name,
      setup(aibitat) {                 // Called when registered with aibitat.use()
        aibitat.function({
          super: aibitat,              // Reference to AIbitat instance
          name: this.name,             // Function name for LLM
          
          // Tells LLM when/why to use this skill
          description: "Analyze text to extract statistics, sentiment, keywords, and other metrics...",
          
          // Examples help LLM understand how to call this
          examples: [
            {
              prompt: "What are the most common words in this text?",
              call: JSON.stringify({
                text: "the text provided by user",
                analysis_type: "keywords",
              }),
            },
            // ... more examples
          ],
          
          // JSON Schema defining input validation
          parameters: {
            $schema: "http://json-schema.org/draft-07/schema#",
            type: "object",
            properties: {
              text: {
                type: "string",
                description: "The text content to analyze.",
              },
              analysis_type: {
                type: "string",
                enum: ["keywords", "sentiment", "statistics", "readability"],
                description: "Type of analysis to perform",
              },
            },
            additionalProperties: false,
          },
          required: ["text", "analysis_type"],
          
          // Main execution function
          handler: async function ({ text = "", analysis_type = "keywords" }) {
            try {
              // Check for duplicate calls
              if (this.tracker.isDuplicate(this.name, { text, analysis_type })) {
                return "This text has already been analyzed.";
              }

              let result;
              switch (analysis_type) {
                case "keywords":
                  result = await this.analyzeKeywords(text);
                  break;
                case "sentiment":
                  result = await this.analyzeSentiment(text);
                  break;
                // ... more cases
              }
              
              return result;
            } catch (error) {
              return `Error during text analysis: ${error.message}`;
            }
          },
        });
      },
    };
  },
};

module.exports = textAnalyzer;
```

### 1.2 Custom Imported Skills

Custom skills are user-imported plugins stored in `server/storage/plugins/agent-skills/{hubId}/`.

**Structure:**
```
server/storage/plugins/agent-skills/
└── my-custom-skill/
    ├── plugin.json          # Configuration metadata
    └── handler.js           # Execution logic
```

**plugin.json:**
```json
{
  "hubId": "my-custom-skill",
  "name": "My Custom Skill",
  "description": "Description of what this skill does",
  "author": "author-name",
  "version": "1.0.0",
  "active": true,
  "author_url": "https://example.com",
  "download_url": "https://example.com/skill.zip"
}
```

**handler.js:**
```javascript
const handler = {
  runtime: {
    handler: async function ({ arg1, arg2 }) {
      try {
        // Skill execution logic
        return "Result of skill execution";
      } catch (error) {
        return `Error: ${error.message}`;
      }
    },
  },
};

module.exports = handler;
```

### 1.3 Agent Flows

Agent flows are complex multi-step automations defined in the system. They follow the same plugin pattern.

### 1.4 MCP Servers

Model Context Protocol servers provide additional tool capabilities through a standardized interface.

---

## 2. Skill Discovery

### 2.1 Built-in Skills Discovery

Built-in skills are discovered at agent initialization through `agentSkillsFromSystemSettings()`:

**Location:** `server/utils/agents/defaults.js`

```javascript
/**
 * Fetches and preloads the names/identifiers for plugins that will be 
 * dynamically loaded later
 * @returns {Promise<string[]>}
 */
async function agentSkillsFromSystemSettings() {
  const systemFunctions = [];

  // Load default enabled built-in skills
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

  // Load user-configured built-in skills
  const _setting = safeJsonParse(
    await SystemSettings.getValueOrFallback(
      { label: "default_agent_skills" },
      "[]"
    ),
    []
  );
  _setting.forEach((skillName) => {
    if (!AgentPlugins.hasOwnProperty(skillName)) return;

    // Handle plugin modules with sub-children (named via ${parent}#${child})
    if (Array.isArray(AgentPlugins[skillName].plugin)) {
      for (const subPlugin of AgentPlugins[skillName].plugin) {
        systemFunctions.push(
          `${AgentPlugins[skillName].name}#${subPlugin.name}`
        );
      }
      return;
    }

    // Handle normal single-stage plugins
    systemFunctions.push(AgentPlugins[skillName].name);
  });
  return systemFunctions;
}
```

**Default enabled built-in skills:**
```javascript
const DEFAULT_SKILLS = [
  AgentPlugins.memory.name,           // Memory management
  AgentPlugins.docSummarizer.name,    // Document summarization
  AgentPlugins.webScraping.name,      // Web content scraping
];
```

### 2.2 Custom Skills Discovery

Custom skills are discovered by scanning the storage directory:

**Location:** `server/utils/agents/imported.js`

```javascript
/**
 * Loads plugins from `plugins` folder in storage that are custom loaded and defined.
 * Only loads plugins that are active: true.
 * @returns {string[]} - array of plugin names to be loaded later.
 */
static activeImportedPlugins() {
  const plugins = [];
  this.checkPluginFolderExists();
  const folders = fs.readdirSync(path.resolve(pluginsPath));
  
  for (const folder of folders) {
    const configLocation = path.resolve(
      pluginsPath,
      normalizePath(folder),
      "plugin.json"
    );
    if (!this.isValidLocation(configLocation)) continue;
    
    const config = safeJsonParse(fs.readFileSync(configLocation, "utf8"));
    // Only include active plugins (marked with active: true)
    if (config.active) plugins.push(`@@${config.hubId}`);
  }
  return plugins;
}
```

**Key points:**
- Scans: `server/storage/plugins/agent-skills/`
- Only loads: Plugins with `"active": true` in `plugin.json`
- Names prefixed with: `@@` to distinguish from built-in skills
- Example: `my-custom-skill` becomes `@@my-custom-skill`

### 2.3 Agent Flows Discovery

**Location:** `server/utils/agentFlows/index.js`

```javascript
static activeFlowPlugins() {
  // Returns only flows with active !== false
}
```

### 2.4 MCP Servers Discovery

**Location:** `server/utils/MCP/index.js`

```javascript
async activeMCPServers() {
  // Returns only running/booted MCP servers
}
```

### 2.5 Combined Discovery

All skill types are collected together in `WORKSPACE_AGENT.getDefinition()`:

**Location:** `server/utils/agents/defaults.js`

```javascript
const WORKSPACE_AGENT = {
  name: "@agent",
  getDefinition: async (provider = null, workspace = null, user = null) => {
    return {
      role: await Provider.systemPrompt({ provider, workspace, user }),
      functions: [
        ...(await agentSkillsFromSystemSettings()),      // Built-in skills
        ...ImportedPlugin.activeImportedPlugins(),       // Custom skills
        ...AgentFlows.activeFlowPlugins(),               // Agent flows
        ...(await new MCPCompatibilityLayer().activeMCPServers()),  // MCP servers
      ],
    };
  },
};
```

---

## 3. Skill Loading into Functions Map

### 3.1 Overview

Skills move from discovery to the `functions` Map through a **plugin registration callback pattern**:

```
Plugin Definition → aibitat.use() → plugin.setup() → aibitat.function() → functions Map
```

### 3.2 Registration Flow

#### Phase 1: Attachment (AgentHandler)

**Location:** `server/utils/agents/index.js` → `AgentHandler#attachPlugins()`

```javascript
async #attachPlugins() {
  // ... build-in skills
  const builtInSkills = await agentSkillsFromSystemSettings();
  for (const skillName of builtInSkills) {
    this.aibitat.use(AgentPlugins[skillName].plugin(callOpts));
  }

  // ... custom skills
  const customSkills = ImportedPlugin.activeImportedPlugins();
  for (const skillIdentifier of customSkills) {
    const hubId = skillIdentifier.replace("@@", "");
    const plugin = ImportedPlugin.loadPluginByHubId(hubId);
    this.aibitat.use(plugin.plugin(callOpts));
  }

  // ... agent flows
  const flows = AgentFlows.activeFlowPlugins();
  for (const flowName of flows) {
    this.aibitat.use(AgentFlows[flowName].plugin());
  }

  // ... MCP servers
  const mcpServers = await new MCPCompatibilityLayer().activeMCPServers();
  for (const serverName of mcpServers) {
    const server = /* get MCP server instance */;
    this.aibitat.use(server.plugin());
  }
}
```

#### Phase 2: AIbitat.use() Registration Hook

**Location:** `server/utils/agents/aibitat/index.js` (lines 69-72)

```javascript
use(plugin) {
  plugin.setup(this);    // ⭐ Pass AIbitat instance to plugin's setup
  return this;           // For method chaining
}
```

#### Phase 3: Plugin Setup and Function Registration

Each plugin's `setup()` method calls `aibitat.function()` with its configuration:

**For built-in skills:**
```javascript
setup(aibitat) {
  aibitat.function({
    super: aibitat,
    name: "text-analyzer",
    description: "...",
    parameters: { /* JSON Schema */ },
    examples: [ /* ... */ ],
    handler: async function (args) { /* execution logic */ },
  });
}
```

**For custom imported skills:**
```javascript
setup(aibitat) {
  const handlerModule = require(`storage/plugins/agent-skills/{hubId}/handler.js`);
  aibitat.function({
    super: aibitat,
    name: this.config.hubId,
    description: this.config.description,
    parameters: this.config.parameters,
    handler: handlerModule.runtime.handler,
  });
}
```

#### Phase 4: Function Storage in Map

**Location:** `server/utils/agents/aibitat/index.js` (lines 988-991)

```javascript
function(functionConfig) {
  this.functions.set(functionConfig.name, functionConfig);  // Store by name
  return this;
}
```

### 3.3 Functions Map Data Structure

After registration, the map contains:

```javascript
// AIbitat.functions = Map {
{
  "text-analyzer": {
    super: AIbitat,
    name: "text-analyzer",
    description: "Analyze text to extract statistics...",
    examples: [...],
    parameters: {
      $schema: "http://json-schema.org/draft-07/schema#",
      type: "object",
      properties: {
        text: { type: "string" },
        analysis_type: { type: "string", enum: [...] }
      },
      required: ["text", "analysis_type"],
    },
    handler: [AsyncFunction],  // The actual execution function
  },

  "web-browsing": { /* ... */ },
  "cli": { /* ... */ },
  "memory": { /* ... */ },
  
  "@@my-custom-skill": {     // Custom skills prefixed with @@
    super: AIbitat,
    name: "@@my-custom-skill",
    description: "Custom skill description",
    parameters: {...},
    handler: [AsyncFunction],  // From handler.js runtime.handler
  },

  "agent-flow#flow-name": { /* ... */ },
  "mcp-server#tool-name": { /* ... */ },
}
// }
```

---

## 4. Functions Given to LLM

### 4.1 Collection Point

Every time the user sends a message, `WORKSPACE_AGENT.getDefinition()` is called to collect current functions:

**Location:** `server/utils/agents/defaults.js`

```javascript
getDefinition: async (provider = null, workspace = null, user = null) => {
  return {
    role: await Provider.systemPrompt({ provider, workspace, user }),
    functions: [
      ...(await agentSkillsFromSystemSettings()),      // Built-in (enabled/not disabled)
      ...ImportedPlugin.activeImportedPlugins(),       // Custom (active: true)
      ...AgentFlows.activeFlowPlugins(),               // Flows (active !== false)
      ...(await new MCPCompatibilityLayer().activeMCPServers()),  // MCP (running)
    ],
  };
};
```

### 4.2 Sending to LLM

**Location:** `server/utils/agents/aibitat/index.js` → `reply()` method (lines 576-622)

```javascript
async reply(route) {
  // ... collect functions based on agent config
  const functions = await this.#collectFunctions(route);

  // Send to provider (OpenAI, Claude, etc.)
  if (this.provider.supportsAgentStreaming) {
    return await this.handleAsyncExecution(
      providerInstance,
      messages,
      functions,      // ⭐ Functions sent with every request
      byAgent
    );
  } else {
    return await this.handleExecution(
      providerInstance,
      messages,
      functions,      // ⭐ Functions sent with every request
      byAgent
    );
  }
}
```

### 4.3 Provider-Specific Formatting

Each provider formats functions for its API:

**Example (OpenAI format):**
```javascript
// What OpenAI receives:
{
  "type": "function",
  "function": {
    "name": "text-analyzer",
    "description": "Analyze text to extract statistics, sentiment, keywords...",
    "parameters": {
      "type": "object",
      "properties": {
        "text": {
          "type": "string",
          "description": "The text content to analyze."
        },
        "analysis_type": {
          "type": "string",
          "enum": ["keywords", "sentiment", "statistics", "readability"],
          "description": "Type of analysis to perform"
        }
      },
      "required": ["text", "analysis_type"]
    }
  }
}
```

**Key point:** Functions are sent with **every user message**, not just at conversation start.

---

## 5. LLM Response Execution

### 5.1 Function Call Response

When the LLM decides to call a function, it responds with:

```javascript
{
  "functionCall": {
    "name": "text-analyzer",
    "arguments": {
      "text": "Some text to analyze",
      "analysis_type": "sentiment"
    }
  }
}
```

### 5.2 Execution Flow

#### For Streaming Providers (e.g., OpenAI, Claude)

**Location:** `server/utils/agents/aibitat/index.js` → `handleAsyncExecution()` (lines 635-724)

```javascript
async handleAsyncExecution(provider, messages, functions, byAgent) {
  // Stream request to LLM with available functions
  const completionStream = await provider.stream(
    messages,
    functions,
    eventHandler
  );

  // Check if LLM returned a function call
  if (completionStream.functionCall) {
    const { name, arguments: args } = completionStream.functionCall;

    // Step 1: Lookup function in registry
    const fn = this.functions.get(name);  // ⭐ Get from functions Map

    // Step 2: Handle hallucination (function not found)
    if (!fn) {
      // Send error back to LLM
      const retryMessages = [
        ...messages,
        { role: "function", content: `Function '${name}' not found.` }
      ];
      return await this.handleAsyncExecution(
        provider,
        retryMessages,
        functions,
        byAgent
      );
    }

    // Step 3: Execute handler
    const result = await fn.handler(args);  // ⭐ Run actual skill code

    // Step 4: Log execution
    this.introspect(`Executing ${name} tool`);

    // Step 5: Add result to message history
    const updatedMessages = [
      ...messages,
      { role: "function", content: result }
    ];

    // Step 6: Recurse - send result back to LLM for next decision
    return await this.handleAsyncExecution(
      provider,
      updatedMessages,      // ⭐ Message history grows
      functions,            // ⭐ Functions re-sent
      byAgent
    );
  }

  // No function call - LLM returned final text response
  return completionStream?.textResponse;
}
```

#### For Non-Streaming Providers (e.g., Ollama, LMStudio)

**Location:** `server/utils/agents/aibitat/index.js` → `handleExecution()` (lines 737-818)

```javascript
async handleExecution(provider, messages, functions, byAgent) {
  // Same logic as async but:
  // 1. Calls provider.complete() instead of provider.stream()
  // 2. Executes synchronously (no streaming events)
  // 3. Same function lookup, execution, and recursion pattern
}
```

### 5.3 Execution Sequence Diagram

```
User Message
    ↓
WORKSPACE_AGENT.getDefinition() → Collect functions
    ↓
provider.stream/complete(messages, functions)
    ↓
LLM decides:
├─→ Call function? 
│   ├─→ Yes: Return { functionCall: { name, arguments } }
│   └─→ No: Return { textResponse: "..." }
│
├─→ Called Function:
│   ├─→ Step 1: this.functions.get(name) → Lookup
│   ├─→ Step 2: fn.handler(arguments) → Execute
│   ├─→ Step 3: Capture result
│   ├─→ Step 4: Add { role: "function", content: result } to messages
│   └─→ Step 5: Recurse with updated messages
│
└─→ No More Function Calls:
    └─→ Return textResponse to user
```

### 5.4 Recursive Tool Calling

The framework supports **chained function calls**:

1. User asks: "Analyze this text and tell me if I should read it"
2. LLM decides: Call `text-analyzer`
3. Skill executes: Returns statistics + sentiment
4. LLM receives result and decides: Call `web-scraping` to get related content
5. Skill executes: Returns scraped content
6. LLM receives all results and returns: Final synthesis to user

```
Message History Example:
[
  { role: "user", content: "Analyze this text..." },
  { role: "assistant", content: "I'll analyze this for you..." },
  { role: "function", content: "Sentiment: Positive, Keywords: ..." },  ← 1st result
  { role: "assistant", content: "Now let me get more context..." },
  { role: "function", content: "Web content found: ..." },               ← 2nd result
  { role: "assistant", content: "Here's my complete analysis..." }      ← Final response
]
```

### 5.5 Error Handling

**Case 1: Function Not Found (Hallucination)**
```javascript
if (!fn) {
  // LLM hallucinated a function name
  // Send error and let LLM retry with correct function
  return await this.handleAsyncExecution(provider, retryMessages, functions);
}
```

**Case 2: Handler Throws Error**
```javascript
// Error caught in handler try-catch
handler: async function (args) {
  try {
    // execution logic
  } catch (error) {
    return `Error: ${error.message}`;  // Returned as result
  }
}
```

**Case 3: Direct Output Flag**
```javascript
// Skip further execution if specified
if (this.skipHandleExecution) {
  this.skipHandleExecution = false;
  return textResponse;  // Return directly without more LLM processing
}
```

### 5.6 Maximum Rounds

Framework has a maximum recursion limit to prevent infinite loops:

```javascript
if (this.hasReachedMaximumRounds()) {
  return "Maximum tool calling rounds reached.";
}
```

Default: 100 rounds (configurable)

---

## Summary: Complete Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│ 1. DEFINITION                                               │
│   Built-in: server/utils/agents/aibitat/plugins/            │
│   Custom:   server/storage/plugins/agent-skills/{hubId}/    │
│   Structure: name, description, parameters, handler         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. DISCOVERY                                                │
│   Built-in:  agentSkillsFromSystemSettings()               │
│   Custom:    ImportedPlugin.activeImportedPlugins()        │
│   Flows:     AgentFlows.activeFlowPlugins()                │
│   MCP:       MCPCompatibilityLayer.activeMCPServers()       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. LOADING                                                  │
│   aibitat.use(plugin)                                       │
│   → plugin.setup(aibitat)                                   │
│   → aibitat.function(config)                                │
│   → functions.set(name, config)                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. LLM DISCOVERY                                            │
│   WORKSPACE_AGENT.getDefinition()                           │
│   Returns: { role, functions: [...] }                       │
│   Sent to LLM with every user message                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. EXECUTION                                                │
│   LLM decides: { functionCall: { name, arguments } }       │
│   Lookup: this.functions.get(name)                          │
│   Execute: fn.handler(arguments)                            │
│   Recurse: Add result to messages, repeat                   │
│   Return: Final textResponse when no more calls             │
└─────────────────────────────────────────────────────────────┘
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `server/utils/agents/aibitat/index.js` | Core AIbitat framework (use, function, reply, handleAsyncExecution, handleExecution) |
| `server/utils/agents/defaults.js` | Skill discovery (agentSkillsFromSystemSettings, WORKSPACE_AGENT) |
| `server/utils/agents/imported.js` | Custom skill loading (ImportedPlugin class) |
| `server/utils/agents/aibitat/plugins/` | Built-in skill definitions |
| `server/storage/plugins/agent-skills/` | Custom imported skills storage |
| `server/utils/agentFlows/index.js` | Agent flows plugin collection |
| `server/utils/MCP/index.js` | MCP servers plugin collection |

