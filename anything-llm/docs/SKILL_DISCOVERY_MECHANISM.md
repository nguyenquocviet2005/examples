# Agent Skill Discovery Mechanism

## Overview

AnythingLLM uses a sophisticated multi-source skill discovery system that combines:
- **Built-in Skills** - Pre-packaged capabilities in the codebase
- **Custom Imported Skills** - User-developed plugins from `storage/plugins/agent-skills/`
- **Agent Flows** - Workflow automation tools
- **MCP Servers** - Model Context Protocol integrations

This document explains how all skill types are discovered, loaded, and made available to agents.

---

## Table of Contents

1. [Discovery Architecture](#discovery-architecture)
2. [Built-in Skills Discovery](#built-in-skills-discovery)
3. [Custom Imported Skills Discovery](#custom-imported-skills-discovery)
4. [Agent Flows Discovery](#agent-flows-discovery)
5. [MCP Servers Discovery](#mcp-servers-discovery)
6. [Skill Loading Pipeline](#skill-loading-pipeline)
7. [Skill Registration with AIbitat](#skill-registration-with-aibitat)
8. [Implementation Details](#implementation-details)

---

## Discovery Architecture

### Initialization Flow

```
Agent Request
    ↓
AgentHandler.createAIbitat()
    ↓
#loadAgents()
    ├─→ Load User Agent
    ├─→ Load Workspace Agent
    └─→ Gather all skill identifiers
         ├─→ agentSkillsFromSystemSettings()    [Built-in]
         ├─→ ImportedPlugin.activeImportedPlugins()   [Custom]
         ├─→ AgentFlows.activeFlowPlugins()    [Flows]
         └─→ MCPCompatibilityLayer.activeMCPServers() [MCP]
    ↓
#attachPlugins()
    ├─→ For each skill identifier:
    │   ├─→ Check type (prefix)
    │   ├─→ Load appropriate plugin
    │   └─→ Register with aibitat.use()
    ↓
Agent Ready with all skills
```

---

## Built-in Skills Discovery

### 1. Registry Location

**Location**: `server/utils/agents/aibitat/plugins/`

Built-in skills are pre-written JavaScript files that implement specific capabilities:

```
server/utils/agents/aibitat/plugins/
├── web-browsing.js          ← Web search capability
├── web-scraping.js          ← Website scraping
├── memory.js                ← Long-term memory
├── summarize.js             ← Document summarization
├── text-analyzer.js         ← Text analysis
├── chat-history.js          ← Chat history management
├── save-file-browser.js     ← File generation
├── rechart.js               ← Chart generation
├── sql-agent/               ← SQL query capability
└── index.js                 ← Master export file
```

### 2. Registration Process

All built-in skills must be exported in `index.js`:

```javascript
// server/utils/agents/aibitat/plugins/index.js
const { webBrowsing } = require("./web-browsing.js");
const { webScraping } = require("./web-scraping.js");
const { docSummarizer } = require("./summarize.js");
const { memory } = require("./memory.js");

module.exports = {
  webBrowsing,
  webScraping,
  docSummarizer,
  memory,
  // ... all other plugins
};
```

This creates the **AgentPlugins** object that the system uses during discovery.

### 3. Discovery Mechanism

#### Default Skills (Always Enabled)

```javascript
// server/utils/agents/defaults.js
const DEFAULT_SKILLS = [
  AgentPlugins.memory.name,           // RAG & long-term memory
  AgentPlugins.docSummarizer.name,    // View & summarize documents
  AgentPlugins.webScraping.name,      // Scrape websites
];
```

These three skills are always available unless explicitly disabled.

#### Discovery Function

```javascript
// server/utils/agents/defaults.js
async function agentSkillsFromSystemSettings() {
  const systemFunctions = [];

  // Step 1: Load disabled skills from database
  const _disabledDefaultSkills = safeJsonParse(
    await SystemSettings.getValueOrFallback(
      { label: "disabled_agent_skills" },
      "[]"
    ),
    []
  );

  // Step 2: Add DEFAULT_SKILLS (minus disabled ones)
  DEFAULT_SKILLS.forEach((skill) => {
    if (!_disabledDefaultSkills.includes(skill)) {
      systemFunctions.push(AgentPlugins[skill].name);
    }
  });

  // Step 3: Load configurable built-in skills from database
  const _setting = safeJsonParse(
    await SystemSettings.getValueOrFallback(
      { label: "default_agent_skills" },
      "[]"
    ),
    []
  );

  // Step 4: Add configurable skills (web-browsing, sql-agent, etc.)
  _setting.forEach((skillName) => {
    if (!AgentPlugins.hasOwnProperty(skillName)) return;

    // Handle parent plugins with sub-plugins
    if (Array.isArray(AgentPlugins[skillName].plugin)) {
      for (const subPlugin of AgentPlugins[skillName].plugin) {
        systemFunctions.push(
          `${AgentPlugins[skillName].name}#${subPlugin.name}`
        );
      }
      return;
    }

    // Single-stage plugin
    systemFunctions.push(AgentPlugins[skillName].name);
  });

  return systemFunctions;
}
```

### 4. Built-in Skills Categories

| Category | Skills | Enabled by Default |
|----------|--------|-------------------|
| **Default** | Memory, Doc Summarizer, Web Scraping | ✅ Yes |
| **Configurable** | Web Search, SQL Agent, Text Analyzer | ❌ Optional |
| **Sub-plugins** | Google Search, SearchAPI, Serper, Bing, etc. | ❌ Optional |

### 5. System Settings Storage

Built-in skill configuration is stored in the database:

```javascript
// Database table: system_settings
{
  label: "default_agent_skills",
  value: "web-browsing,sql-agent"  // CSV of enabled configurable skills
}

{
  label: "disabled_agent_skills",
  value: "memory"  // CSV of disabled default skills
}
```

---

## Custom Imported Skills Discovery

### 1. Storage Location

Custom skills are stored in the file system:

```
server/storage/plugins/agent-skills/
├── text-analyzer-skill/
│   ├── plugin.json          ← Configuration & metadata
│   ├── handler.js           ← Implementation logic
│   └── README.md            ← Documentation
├── sentiment-analyzer/
│   ├── plugin.json
│   ├── handler.js
│   └── README.md
└── [other-skills]/
```

**Storage Path Resolution**:
```javascript
const pluginsPath = process.env.NODE_ENV === "development"
  ? path.resolve(__dirname, "../../storage/plugins/agent-skills")
  : path.resolve(process.env.STORAGE_DIR, "plugins", "agent-skills");
```

### 2. Plugin Configuration File

Each custom skill requires a `plugin.json`:

```json
{
  "hubId": "text-analyzer-skill",
  "name": "Text Analyzer",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "Analyze text to extract statistics, sentiment, keywords, and readability metrics.",
  "long_description": "A comprehensive text analysis tool...",
  "verified": false,
  "active": true,
  "tags": ["text-analysis", "nlp", "statistics"],
  "icon": "https://example.com/icon.png",
  "preview": "https://example.com/preview.png",
  "capabilities": [
    "keyword-extraction",
    "sentiment-analysis",
    "readability-scoring",
    "text-statistics"
  ],
  "permissions": ["read:documents"],
  "entrypoint": {
    "handler": "handler.js",
    "params": {
      "text": {
        "type": "string",
        "description": "The text content to analyze"
      },
      "analysisType": {
        "type": "string",
        "description": "Type of analysis: 'sentiment', 'keywords', 'readability', or 'statistics'",
        "enum": ["sentiment", "keywords", "readability", "statistics"]
      }
    }
  }
}
```

### 3. Discovery Function

```javascript
// server/utils/agents/imported.js
class ImportedPlugin {
  static activeImportedPlugins() {
    const plugins = [];
    
    // Ensure plugins directory exists
    this.checkPluginFolderExists();
    
    // Scan the plugins directory
    const folders = fs.readdirSync(path.resolve(pluginsPath));
    
    for (const folder of folders) {
      // Construct path to plugin.json
      const configLocation = path.resolve(
        pluginsPath,
        normalizePath(folder),
        "plugin.json"
      );
      
      // Validate path is within allowed directory
      if (!this.isValidLocation(configLocation)) continue;
      
      // Read and parse plugin.json
      const config = safeJsonParse(
        fs.readFileSync(configLocation, "utf8")
      );
      
      // Only include active plugins
      if (config.active) {
        // Prefix with @@ to identify as custom skill
        plugins.push(`@@${config.hubId}`);
      }
    }
    
    return plugins;
  }
}
```

### 4. Key Requirements

For a custom skill to be discovered:

| Requirement | Details |
|-------------|---------|
| **Folder name** | Must match `hubId` in plugin.json |
| **plugin.json** | Must exist and be valid JSON |
| **"active"** | Must be set to `true` in plugin.json |
| **handler.js** | Must exist and export `runtime` object |
| **Prefix** | Identified by `@@` prefix during loading |

### 5. Handler Implementation

```javascript
// server/storage/plugins/agent-skills/text-analyzer-skill/handler.js
const handler = {
  runtime: {
    handler: async function ({ text = "", analysisType = "sentiment" }) {
      try {
        let result;
        
        switch (analysisType) {
          case "keywords":
            result = extractKeywords(text);
            break;
          case "sentiment":
            result = analyzeSentiment(text);
            break;
          // ... more cases
        }
        
        // Log to agent framework
        if (this.super?.introspect) {
          this.super.introspect(
            `${this.caller}: Analyzed text for ${analysisType}`
          );
        }
        
        return result;
      } catch (error) {
        return `Error: ${error.message}`;
      }
    },
  },
};

module.exports = handler;
```

### 6. Loading Process

```javascript
// server/utils/agents/index.js
async #attachPlugins(args) {
  for (const name of this.#funcsToLoad) {
    // Load imported plugin (marked by @@ prefix)
    if (name.startsWith("@@")) {
      const hubId = name.replace("@@", "");
      
      // Validate handler exists
      const valid = ImportedPlugin.validateImportedPluginHandler(hubId);
      if (!valid) {
        this.log(`Plugin ${hubId} handler not found. Skipping.`);
        continue;
      }
      
      // Load the plugin
      const plugin = ImportedPlugin.loadPluginByHubId(hubId);
      
      // Parse setup arguments from plugin config
      const callOpts = plugin.parseCallOptions();
      
      // Register with AIbitat
      this.aibitat.use(plugin.plugin(callOpts));
      
      this.log(`Attached ${plugin.name} (${hubId}) imported plugin`);
      continue;
    }
    
    // ... handle other skill types
  }
}
```

---

## Agent Flows Discovery

### Overview

Agent Flows are pre-configured automation workflows that can be created through the UI.

### Discovery

```javascript
// server/utils/agentFlows/index.js
static activeFlowPlugins() {
  // Scans database for flows marked as active
  // Returns: ["@@flow_uuid-1234", "@@flow_uuid-5678", ...]
}
```

### Identification

- **Prefix**: `@@flow_`
- **Format**: `@@flow_{uuid}`
- **Storage**: Database (not filesystem)

---

## MCP Servers Discovery

### Overview

MCP (Model Context Protocol) servers provide additional capabilities via external protocols.

### Discovery

```javascript
// server/utils/MCP/index.js
async activeMCPServers() {
  // Scans for configured MCP servers
  // Returns: ["@@mcp_server_name:tool1", "@@mcp_server_name:tool2", ...]
}
```

### Identification

- **Prefix**: `@@mcp_`
- **Format**: `@@mcp_{server_name}:{tool_name}`
- **Sub-tools**: Each server can have multiple tools

---

## Skill Loading Pipeline

### Complete Load Sequence

```
1. Agent Request Received
   ↓
2. createAIbitat() called
   ↓
3. #loadAgents()
   ├─→ Create USER_AGENT
   ├─→ Create WORKSPACE_AGENT
   └─→ Collect skill identifiers:
       this.#funcsToLoad = [
         "memory",                    // Built-in skill
         "web-scraping",              // Built-in skill
         "web-browsing#google-search",// Built-in sub-plugin
         "@@text-analyzer-skill",     // Custom skill
         "@@flow_uuid-1234",          // Agent flow
         "@@mcp_server:tool1"         // MCP tool
       ]
   ↓
4. #attachPlugins()
   For each skill in #funcsToLoad:
     a. Check prefix and type
     b. Load appropriate plugin
     c. Create plugin instance
     d. Register with aibitat.use()
   ↓
5. startAgentCluster()
   ├─→ Setup channel
   ├─→ Setup event handlers
   └─→ Ready for chat
   ↓
6. Agent Ready!
```

### Skill Type Detection

```javascript
if (name.includes("#")) {
  // Sub-plugin: "parent#child"
} else if (name.startsWith("@@flow_")) {
  // Agent flow: "@@flow_uuid"
} else if (name.startsWith("@@mcp_")) {
  // MCP server: "@@mcp_server:tool"
} else if (name.startsWith("@@")) {
  // Custom imported skill: "@@hubId"
} else {
  // Built-in skill: "skill-name"
}
```

---

## Skill Registration with AIbitat

### AIbitat Function Definition

Each skill, regardless of source, is registered as a function in AIbitat:

```javascript
aibitat.function({
  name: "text-analyzer",                    // Unique identifier
  description: "Analyze text for statistics, sentiment, keywords, and readability",
  
  parameters: {                             // OpenAI JSON Schema format
    $schema: "http://json-schema.org/draft-07/schema#",
    type: "object",
    properties: {
      text: {
        type: "string",
        description: "The text content to analyze"
      },
      analysisType: {
        type: "string",
        enum: ["sentiment", "keywords", "readability", "statistics"],
        description: "Type of analysis to perform"
      }
    },
    additionalProperties: false
  },
  
  examples: [                               // Usage examples for LLM
    {
      prompt: "Analyze the sentiment of this text",
      call: JSON.stringify({
        text: "user-provided-text",
        analysisType: "sentiment"
      })
    }
  ],
  
  handler: async function(params) {         // Actual implementation
    // Execute skill logic
    return result;
  }
});
```

### Skill Invocation

When the agent decides to use a skill:

```
1. Agent generates function call
   ↓
2. AIbitat identifies skill by name
   ↓
3. Validates parameters against schema
   ↓
4. Calls handler() with parameters
   ↓
5. Receives result
   ↓
6. Continues conversation with result
```

---

## Implementation Details

### File Structure Overview

```
AnythingLLM/
├── server/
│   ├── utils/agents/
│   │   ├── index.js                 ← AgentHandler class
│   │   ├── defaults.js              ← Built-in skill discovery
│   │   ├── imported.js              ← Custom skill discovery
│   │   ├── aibitat/
│   │   │   ├── index.js             ← AIbitat framework
│   │   │   └── plugins/
│   │   │       ├── index.js         ← Built-in skills registry
│   │   │       ├── web-browsing.js
│   │   │       ├── web-scraping.js
│   │   │       └── ... more skills
│   │   └── agentFlows/
│   │       └── index.js             ← Flow discovery
│   └── storage/
│       └── plugins/agent-skills/    ← Custom skills storage
│           ├── text-analyzer-skill/
│           │   ├── plugin.json
│           │   └── handler.js
│           └── ... more custom skills
│
├── frontend/
│   └── src/pages/Admin/Agents/
│       ├── index.jsx                ← Admin UI
│       └── skills.js                ← Skill configuration
```

### Discovery Timing

| Type | Discovery Time | Caching |
|------|---|---|
| **Built-in Skills** | Server startup | Cached in memory |
| **Custom Skills** | Per-request | Filesystem scan each time |
| **Agent Flows** | Per-request | Database query each time |
| **MCP Servers** | Per-request | Configuration scan each time |

> **Note**: Custom skills filesystem scan is relatively fast due to small number of plugins, but consider caching for high-frequency usage.

### System Settings Integration

Built-in skill configuration is managed via the system settings:

```javascript
// Enable/disable specific built-in skills
await SystemSettings.updateSettings({
  default_agent_skills: "web-browsing,sql-agent",
  disabled_agent_skills: "memory"
});
```

These settings are read during every agent initialization.

---

## Best Practices

### For Built-in Skills

1. ✅ Export in `plugins/index.js`
2. ✅ Follow naming convention: lowercase with hyphens
3. ✅ Use `Deduplicator` to prevent duplicate function calls
4. ✅ Include comprehensive examples
5. ✅ Use `aibitat.function()` for registration

### For Custom Skills

1. ✅ Set `"active": true` in plugin.json
2. ✅ Folder name must match hubId
3. ✅ Export `runtime.handler` from handler.js
4. ✅ Use proper error handling
5. ✅ Include `entrypoint.params` with complete schema
6. ✅ Log via `this.super.introspect()` for debugging
7. ✅ Test with actual agent requests

### Error Handling

```javascript
handler: async function(params) {
  try {
    // Skill logic
    if (this.super?.introspect) {
      this.super.introspect(`Success message`);
    }
    return result;
  } catch (error) {
    if (this.super?.introspect) {
      this.super.introspect(`Error: ${error.message}`);
    }
    return `Error during operation: ${error.message}`;
  }
}
```

---

## Troubleshooting

### Custom Skill Not Appearing

1. Check `plugin.json` exists in correct location
2. Verify `"active": true` in plugin.json
3. Confirm `handler.js` exists
4. Check handler exports `runtime.handler`
5. Verify JSON syntax in plugin.json (use JSON validator)
6. Check hubId matches folder name

### Built-in Skill Not Available

1. Check skill is exported in `plugins/index.js`
2. Verify not disabled in system settings
3. Confirm skill name matches exactly
4. Check no typos in skill identifier

### Skill Not Executing Correctly

1. Check parameter schema matches OpenAI format
2. Verify handler function signature
3. Check error handling in handler
4. Review logs for error messages
5. Test with simpler input first

---

## Summary

AnythingLLM's skill discovery system provides:

- **Multiple skill sources** for maximum flexibility
- **Automatic detection** of custom skills via filesystem scanning
- **Database-backed configuration** for built-in skills
- **Consistent registration** through AIbitat framework
- **Extensible architecture** for adding new skill types

By understanding this mechanism, developers can:
- Create custom skills that are automatically discovered
- Configure built-in skills through UI
- Debug skill loading issues effectively
- Extend the framework with new capabilities
