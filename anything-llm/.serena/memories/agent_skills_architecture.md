# AnythingLLM Agent Skills Architecture

## Overview
Agent skills are extensible plugins that enhance the `@agent` capabilities in AnythingLLM. The system uses a plugin architecture where skills can be:
1. **Built-in Default Skills** - Always available and mostly enabled by default
2. **Configurable Skills** - Built-in but can be toggled on/off
3. **Imported Custom Skills** - Community-created skills imported from the Community Hub

## Architecture Layers

### 1. Backend (Server-Side)

#### Skill Definition & Loading
- **File**: `server/utils/agents/defaults.js`
- **Key Data Structures**:
  - `DEFAULT_SKILLS`: Array of always-available skills (memory, docSummarizer, webScraping)
  - `WORKSPACE_AGENT.getDefinition()`: Assembles all active skills for the agent
  - `agentSkillsFromSystemSettings()`: Dynamically loads enabled skills based on system settings

#### System Settings Integration
- **File**: `server/models/systemSettings.js`
- **Settings Keys**:
  - `default_agent_skills`: Comma-separated list of enabled configurable skills (JSON array)
  - `disabled_agent_skills`: Comma-separated list of disabled default skills (JSON array)
  - `imported_agent_skills`: Auto-populated list of imported plugins from storage

#### Skill Plugin System
- **File**: `server/utils/agents/aibitat/plugins/index.js`
- **Built-in Plugins**:
  - `web-browsing`: Search using various engines (Google, Bing, SearXNG, etc.)
  - `web-scraping`: Visit and extract website content
  - `rag-memory`: Search local documents or store content in vector database
  - `document-summarizer`: Summarize workspace documents
  - `save-file-to-browser`: Generate files downloadable to client
  - `create-chart`: Generate chart visualizations
  - `sql-agent`: Query SQL databases
  - `chat-history`: Access conversation history
  - `rechart`: Advanced charting

#### AIbitat Framework
- **File**: `server/utils/agents/aibitat/index.js`
- **Core Concept**: Multi-agent orchestration framework
- **Key Methods**:
  - `agent()`: Register named agent with configuration
  - `function()`: Register a callable function/skill
  - `channel()`: Create communication channels between agents
  - `getAgentConfig()`: Retrieve agent definition with role and functions

#### Imported Plugin System
- **File**: `server/utils/agents/imported.js`
- **Storage**: `storage/plugins/agent-skills/{hubId}/`
- **Plugin Structure**:
  - `plugin.json`: Configuration metadata (name, description, active flag)
  - `handler.js`: Skill implementation
- **Loading**: 
  - `activeImportedPlugins()`: Returns list of active imported plugins
  - `loadPluginByHubId()`: Load specific plugin from storage
  - `importCommunityItemFromUrl()`: Download and import from Community Hub

#### Skill Execution Flow
1. **Function Definition**: Each skill defines:
   - `name`: Unique identifier
   - `description`: What the skill does
   - `parameters`: JSON Schema for input validation
   - `examples`: Sample prompts and calls
   - `handler()`: Async function that executes the skill

2. **AI Invocation**: LLM sees skills in its function list and can call them by name
3. **Handler Execution**: When called, the handler receives parameters and returns response
4. **Tool Use Pattern**: Follows OpenAI function_calling/tool_use pattern

### 2. Frontend (Client-Side)

#### Skill Management UI
- **File**: `frontend/src/pages/Admin/Agents/index.jsx`
- **Features**:
  - Display default skills (always visible)
  - Display configurable skills (can be toggled)
  - Display imported custom skills
  - UI for enabling/disabling skills

#### Skill Definitions (UI)
- **File**: `frontend/src/pages/Admin/Agents/skills.js`
- **Categories**:
  - `defaultSkills`: Pre-enabled, cannot be completely disabled (only disableable)
  - `configurableSkills`: Optional skills that can be toggled

#### Skill Configuration Panels
- `DefaultSkillPanel`: Display-only for built-in skills
- `GenericSkillPanel`: Toggle UI for optional skills
- `AgentWebSearchSelection`: Configure web search provider
- `AgentSQLConnectorSelection`: Configure SQL database connections
- `ImportedSkillConfig`: Configure imported custom skills

#### Community Hub Integration
- **Import Flow**: 
  1. User finds skill in Community Hub
  2. Import triggers download of zipped skill
  3. Skill extracted to `storage/plugins/agent-skills/{hubId}/`
  4. System loads and activates skill

## Data Flow Diagram

```
User Request
    ↓
Chat Message → @agent mention
    ↓
WORKSPACE_AGENT.getDefinition()
    ↓
┌─────────────────────────────────────┐
│ Assemble Function List:             │
├─────────────────────────────────────┤
│ 1. DEFAULT_SKILLS (always present)  │
│    - rag-memory                     │
│    - document-summarizer           │
│    - web-scraping                  │
├─────────────────────────────────────┤
│ 2. System Settings Skills           │
│    - Load from "default_agent_skills"
│    - Skip those in "disabled_*"    │
│    - Includes: web-browsing, sql-agent
├─────────────────────────────────────┤
│ 3. Imported Plugins                 │
│    - Load from storage/plugins/...  │
│    - Must have active: true         │
├─────────────────────────────────────┤
│ 4. MCP Servers                      │
│    - Model Context Protocol tools   │
│    - Agent Flows                    │
└─────────────────────────────────────┘
    ↓
Send to LLM with functions schema
    ↓
LLM Decides to call skill
    ↓
AIbitat executes function handler
    ↓
Skill runs and returns result
    ↓
Result sent to LLM for processing
    ↓
Response sent to user
```

## Skill Structure (Example: web-browsing)

```javascript
const webBrowsing = {
  name: "web-browsing",                    // Skill identifier
  startupConfig: { params: {} },          // Optional startup params
  plugin: function() {
    return {
      name: this.name,
      setup(aibitat) {
        aibitat.function({
          name: "web-browsing",
          description: "Search query using search engine",
          parameters: {                     // JSON Schema
            type: "object",
            properties: {
              query: { type: "string" }
            }
          },
          examples: [                       // Few-shot examples for LLM
            {
              prompt: "What is AnythingLLM?",
              call: JSON.stringify({ query: "AnythingLLM" })
            }
          ],
          handler: async function({ query }) {
            // Execute the skill
            return await this.search(query);
          },
          search: async function(query) {
            // Search implementation
          }
        });
      }
    }
  }
}
```

## Key Implementation Details

### 1. Three-Tier Skill Architecture
- **Default**: Always present, can be disabled
- **Configurable**: Opt-in, database-driven enablement
- **Imported**: Dynamically loaded from filesystem

### 2. System Settings Storage
- Skills stored as JSON arrays in `systemSettings` table
- `default_agent_skills`: CSV string converted to/from JSON
- `disabled_agent_skills`: CSV string converted to/from JSON
- Validators ensure data integrity

### 3. Dynamic Loading
- Skills loaded at request time via `agentSkillsFromSystemSettings()`
- Imported plugins lazy-loaded from `require.cache`
- No restart needed for imports (if cache cleared)

### 4. Security Considerations
- Imported skills execute arbitrary code
- UI warns users: "Only import skills you trust"
- Skills can access AnythingLLM instance system
- Recommend reviewing skill code before import

### 5. Skill Chaining
- One skill can use another via AIbitat context
- Tracker prevents duplicate executions
- Handler function has access to `aibitat` context

## Extension Points

### Creating Custom Skills
1. **Create handler.js** with skill logic
2. **Create plugin.json** with metadata
3. **Zip and host** for Community Hub
4. **Users import** from UI

### Modifying Built-in Skills
- Edit files in `server/utils/agents/aibitat/plugins/`
- Restart server to reload
- Export in `index.js`

### Adding New Configurable Skill
1. Create plugin file in `plugins/`
2. Export in `plugins/index.js`
3. Add to `AgentPlugins` mapping
4. Add UI panel in frontend
