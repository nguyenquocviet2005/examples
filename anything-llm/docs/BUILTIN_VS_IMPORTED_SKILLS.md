# Built-in vs Imported Skills: Complete Guide

## Quick Comparison

| Aspect | Built-in Skill | Imported Skill |
|--------|---|---|
| Location | `server/utils/agents/aibitat/plugins/` | `storage/plugins/agent-skills/{hubId}/` |
| Config File | `plugin.json` optional (metadata only) | `plugin.json` required |
| Handler | `skill-name.js` in plugins directory | `handler.js` in plugin folder |
| Registration | Exported in `plugins/index.js` | Auto-loaded from filesystem |
| Loading | At server startup | On-demand from storage |
| Distribution | Part of source code | Imported from Community Hub |
| Updates | Require code changes | Can be swapped without restart |

## Built-in Skill Structure

### Location
```
server/utils/agents/aibitat/plugins/
├── text-analyzer.js          ← Skill implementation
├── web-browsing.js
├── memory.js
└── index.js                  ← Must export skill
```

### Example: Built-in Skill File

**File**: `server/utils/agents/aibitat/plugins/text-analyzer.js`

```javascript
const { Deduplicator } = require("../utils/dedupe");

const textAnalyzer = {
  name: "text-analyzer",
  startupConfig: { params: {} },
  plugin: function () {
    return {
      name: this.name,
      setup(aibitat) {
        aibitat.function({
          // ... skill definition
        });
      },
    };
  },
};

module.exports = { textAnalyzer };
```

### Registration

**File**: `server/utils/agents/aibitat/plugins/index.js`

```javascript
const { textAnalyzer } = require("./text-analyzer.js");

module.exports = {
  textAnalyzer,
  [textAnalyzer.name]: textAnalyzer,
  // ... other skills
};
```

### No plugin.json Needed

Built-in skills don't require `plugin.json` because:
- They're part of the source code
- Metadata is in the skill definition itself
- They're always available to all instances
- Configuration is in system settings database

---

## Imported Skill Structure

### Directory Layout

```
storage/plugins/agent-skills/
└── text-analyzer-skill/          ← hubId folder
    ├── plugin.json               ← REQUIRED metadata
    └── handler.js                ← REQUIRED handler
```

### plugin.json: Metadata File

**Purpose**: Describes the skill to the system

```json
{
  "hubId": "text-analyzer-skill",
  "name": "Text Analyzer",
  "version": "1.0.0",
  "author": "AnythingLLM",
  "description": "Analyze text for statistics, sentiment, and keywords.",
  "long_description": "Comprehensive text analysis tool...",
  "verified": false,
  "active": true,
  "tags": ["text-analysis", "nlp"],
  "icon": "https://example.com/icon.png",
  "preview": "https://example.com/preview.png",
  "capabilities": [
    "keyword-extraction",
    "sentiment-analysis",
    "readability-scoring"
  ],
  "permissions": ["read:documents"],
  "configuration": {
    "minTextLength": {
      "type": "number",
      "description": "Minimum text length",
      "default": 10
    }
  }
}
```

### handler.js: Implementation File

**Purpose**: Contains the actual skill logic

```javascript
const handler = {
  setup(aibitat) {
    aibitat.function({
      name: "text-analyzer",
      description: "Analyze text...",
      parameters: { /* ... */ },
      handler: async function({ text, analysis_type }) {
        // Implementation here
        return result;
      },
    });
  },
};

module.exports = handler;
```

### Key Differences in Handler

| Aspect | Built-in | Imported |
|--------|----------|----------|
| Module wrapper | Full plugin object | Just `handler` export |
| Setup | Defined in plugin | Defined in handler.setup |
| Loading | Via require in index.js | Via require.cache with path |
| Error isolation | Stops server if broken | Graceful fallback |

---

## Loading Process

### Built-in Skills

```
Server Startup
    ↓
AIbitat initializes
    ↓
plugins/index.js imported
    ↓
Each skill's plugin() called
    ↓
Each skill's setup(aibitat) called
    ↓
Functions registered in aibitat
    ↓
Skills ready to use
```

### Imported Skills

```
Agent definition requested
    ↓
agentSkillsFromSystemSettings() called
    ↓
ImportedPlugin.activeImportedPlugins() called
    ↓
List plugins in storage/plugins/agent-skills/
    ↓
For each active plugin:
  - Load plugin.json
  - require handler.js
  - Clear require.cache
  - Call handler.setup(aibitat)
    ↓
Skills registered dynamically
```

**Code Reference**: `server/utils/agents/imported.js`

```javascript
static activeImportedPlugins() {
  const plugins = [];
  const folders = fs.readdirSync(pluginsPath);
  
  for (const folder of folders) {
    const configPath = path.resolve(pluginsPath, folder, "plugin.json");
    if (!this.isValidLocation(configPath)) continue;
    
    const config = safeJsonParse(fs.readFileSync(configPath, "utf8"));
    if (config.active) plugins.push(`@@${config.hubId}`);  // @@prefix for imported
  }
  return plugins;
}
```

---

## When to Use Each

### Create Built-in Skill When:
- ✅ Core functionality for all instances
- ✅ No external dependencies required
- ✅ Part of AnythingLLM package
- ✅ Maintained by core team
- ✅ Should always be available

**Examples**: Memory, Web Search, SQL Agent, Document Summarizer

### Create Imported Skill When:
- ✅ Optional community feature
- ✅ User can choose to install
- ✅ Specialized/domain-specific
- ✅ Third-party maintained
- ✅ Can be updated independently
- ✅ Shared via Community Hub

**Examples**: Custom integrations, specialized analyzers, domain tools

---

## Development Workflow

### For Built-in Skills

1. Create `skill-name.js` in `plugins/` directory
2. Export in `plugins/index.js`
3. Add to frontend UI in `skills.js`
4. Restart server
5. Test in chat

### For Imported Skills

1. Create folder: `storage/plugins/agent-skills/{hubId}/`
2. Create `plugin.json` with metadata
3. Create `handler.js` with implementation
4. Package as zip (optional, for Community Hub)
5. User imports via UI or manual upload
6. No restart needed
7. Test in chat

---

## plugin.json Fields Reference

### Required Fields

```json
{
  "hubId": "unique-skill-id",
  "name": "Display Name",
  "version": "1.0.0",
  "description": "Short description",
  "active": true,
  "handler": "handler.js"
}
```

### Optional Fields

```json
{
  "author": "Author Name",
  "long_description": "Longer description...",
  "verified": false,
  "tags": ["tag1", "tag2"],
  "icon": "https://...",
  "preview": "https://...",
  "capabilities": ["cap1", "cap2"],
  "permissions": ["read:documents"],
  "configuration": { /* config schema */ },
  "license": "MIT",
  "homepage": "https://...",
  "repository": "https://..."
}
```

### Configuration Field

Define skill parameters users can customize:

```json
"configuration": {
  "paramName": {
    "type": "string|number|boolean|select",
    "description": "What this does",
    "default": "default_value",
    "options": ["opt1", "opt2"]  // for select type
  }
}
```

---

## File System Paths

### Built-in Skills Storage
```
/server/utils/agents/aibitat/plugins/
```

**Why**: Part of source code, committed to git

### Imported Skills Storage
```
Development:
/storage/plugins/agent-skills/{hubId}/

Production:
${STORAGE_DIR}/plugins/agent-skills/{hubId}/
```

**Why**: User-provided, not version controlled

---

## Example: Complete Imported Skill

See: `docs/EXAMPLE_CUSTOM_SKILL_STRUCTURE/`

- `plugin.json` - Full metadata example
- `handler.js` - Complete implementation

---

## Migration: Built-in to Imported

If you want to convert a built-in skill to an imported one:

1. **Extract the handler logic** from `plugin.js`
2. **Create plugin.json** with metadata
3. **Create handler.js** with setup function
4. **Move to storage** directory
5. **Remove from plugins/index.js**
6. **Update frontend** references

---

## Security Considerations

### Built-in Skills
- ✅ Part of code review process
- ✅ Tested before release
- ✅ Trusted source

### Imported Skills
- ⚠️ User-uploaded code execution
- ⚠️ UI warning: "Only import skills you trust"
- ⚠️ Should review code before importing
- ⚠️ Can access full server context

---

## Troubleshooting

### Built-in Skill Not Appearing
- [ ] Check export in `plugins/index.js`
- [ ] Verify `name` property matches
- [ ] Check frontend `skills.js` configuration
- [ ] Restart server

### Imported Skill Not Loading
- [ ] Check `plugin.json` exists in folder
- [ ] Verify `active: true` in plugin.json
- [ ] Check folder is in `storage/plugins/agent-skills/`
- [ ] Verify `handler.js` exists and valid
- [ ] Check server logs for require errors

### Handler Not Being Called
- [ ] Verify `setup()` function exists
- [ ] Check `aibitat.function()` is called in setup
- [ ] Verify function `name` is unique
- [ ] Check JSON Schema is valid

---

## Related Documentation

- [Example Agent Skill](./EXAMPLE_AGENT_SKILL.md) - Built-in skill walkthrough
- [Skill Developer Guide](./SKILL_DEVELOPER_GUIDE.md) - Quick reference
- [Imported Skills Code](../server/utils/agents/imported.js)
- [Built-in Plugins Code](../server/utils/agents/aibitat/plugins/index.js)
- [System Settings](../server/models/systemSettings.js)
