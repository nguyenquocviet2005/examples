# Agent Skill Developer Quick Reference

## Quick Start Checklist

- [ ] Create new file: `server/utils/agents/aibitat/plugins/your-skill.js`
- [ ] Export skill object with `name`, `startupConfig`, and `plugin` function
- [ ] Define `aibitat.function()` with description, parameters, and handler
- [ ] Register in `server/utils/agents/aibitat/plugins/index.js`
- [ ] Add UI in `frontend/src/pages/Admin/Agents/skills.js` (if configurable)
- [ ] Test with `@agent` in chat

## Minimal Skill Template

```javascript
const { Deduplicator } = require("../utils/dedupe");

const mySkill = {
  name: "my-skill",
  startupConfig: { params: {} },
  plugin: function () {
    return {
      name: this.name,
      setup(aibitat) {
        aibitat.function({
          super: aibitat,
          tracker: new Deduplicator(),
          name: this.name,
          
          description: "What this skill does",
          
          examples: [
            {
              prompt: "Example user request",
              call: JSON.stringify({ param1: "value1" }),
            },
          ],
          
          parameters: {
            $schema: "http://json-schema.org/draft-07/schema#",
            type: "object",
            properties: {
              param1: {
                type: "string",
                description: "Description of param1",
              },
            },
            additionalProperties: false,
          },
          required: ["param1"],
          
          handler: async function ({ param1 }) {
            try {
              if (this.tracker.isDuplicate(this.name, { param1 })) {
                return "Already done this.";
              }

              this.super.introspect(
                `${this.caller}: Executing ${this.name}.`
              );

              const result = await this.executeLogic(param1);
              
              this.tracker.trackRun(this.name, { param1 });
              return result;
            } catch (error) {
              this.super.handlerProps.log(
                `${this.name} error: ${error.message}`
              );
              return `Error: ${error.message}`;
            }
          },

          executeLogic: async function (param1) {
            // Your logic here
            return "Result";
          },
        });
      },
    };
  },
};

module.exports = { mySkill };
```

## Handler Context

```javascript
// Available in handler function:
this.super              // AIbitat instance
this.super.socket       // Send real-time updates
this.super.introspect() // Log action
this.super.handlerProps // Config
this.caller             // Calling agent name
this.tracker            // Dedupe tracker
this.name               // Skill name
```

## Common Operations

### Send Message to Frontend
```javascript
this.super.socket.send("eventName", { data: "payload" });
```

### Log for Debugging
```javascript
this.super.introspect(`${this.caller}: Doing something`);
this.super.handlerProps.log(`Error occurred`);
```

### Prevent Duplicate Calls
```javascript
if (this.tracker.isDuplicate(this.name, params)) return "Done already";
this.tracker.trackRun(this.name, params);
```

### Return Formatted Response
```javascript
return `**Bold Title:**\n- Item 1\n- Item 2`;
```

### Parameter Types

```javascript
properties: {
  stringParam: { type: "string" },
  numberParam: { type: "number" },
  boolParam: { type: "boolean" },
  selectParam: { 
    type: "string", 
    enum: ["option1", "option2"] 
  },
  arrayParam: { 
    type: "array", 
    items: { type: "string" } 
  },
}
```

## Registration Steps

### 1. Add Import
```javascript
// server/utils/agents/aibitat/plugins/index.js
const { mySkill } = require("./my-skill.js");
```

### 2. Add to Exports
```javascript
module.exports = {
  // ... other skills
  mySkill,
  [mySkill.name]: mySkill,
};
```

### 3. Add to Frontend (optional)
```javascript
// frontend/src/pages/Admin/Agents/skills.js
export const configurableSkills = {
  "my-skill": {
    title: "My Skill",
    description: "What it does",
    component: GenericSkillPanel,
    skill: "my-skill",
  },
};
```

## Special Attributes (Advanced)

Return structured data to frontend:
```javascript
this.super._replySpecialAttributes = {
  saveAsType: "customType",
  storedResponse: (additionalText = "") =>
    JSON.stringify({ result, additionalText }),
  postSave: () => {
    this.tracker.removeUniqueConstraint(this.name);
  },
};
```

## Testing

1. Navigate to Admin → Agents → Agent Skills
2. Verify skill appears in configurable skills
3. Toggle skill to enabled
4. In chat, prompt: `@agent: [request that uses skill]`
5. Check logs in server console for `introspect` messages

## Debugging Tips

- Check `this.super.handlerProps.log()` output in server console
- Verify skill appears in function list: run `WORKSPACE_AGENT.getDefinition()`
- Check JSON Schema syntax for parameters
- Use try-catch to catch errors early
- Test async operations with proper await

## Examples in Codebase

| Skill | File | Pattern |
|-------|------|---------|
| Text Analyzer | `text-analyzer.js` | Analysis/Processing |
| Web Browsing | `web-browsing.js` | External API calls |
| Memory | `memory.js` | RAG/Vector DB |
| Save File | `save-file-browser.js` | Socket communication |
| Create Chart | `rechart.js` | Data visualization |
| SQL Agent | `sql-agent/index.js` | Database queries |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Function not appearing" | Not exported in index.js | Add to module.exports |
| "Handler not called" | JSON Schema invalid | Validate against spec |
| "Duplicate calls ignored" | Deduplication active | Check tracker logic |
| "Socket send fails" | Event name wrong | Check case sensitivity |
| "Async timeout" | No await | Use async/await properly |

## Next Steps

1. Review `text-analyzer.js` example
2. Read `EXAMPLE_AGENT_SKILL.md` for detailed guide
3. Check existing skills for patterns
4. Create your skill following template
5. Test in chat
6. Share with community!
