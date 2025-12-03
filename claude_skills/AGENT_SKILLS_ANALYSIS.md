# Anthropic Agent Skills - Under the Hood Analysis

## Overview
Agent Skills in the Anthropic Python library allow you to extend Claude's capabilities by providing pre-packaged functionality (like creating presentations, working with documents, etc.) that Claude can use within a sandboxed container environment.

## Architecture

### 1. **Beta Feature Structure**
Skills are part of Anthropic's beta features and require specific beta flags to use:
- `skills-2025-10-02` - The skills feature beta version
- `code-execution-2025-08-25` - Often used alongside for code execution capabilities

### 2. **Key Components**

#### A. Skills API (`anthropic/resources/beta/skills/`)
Located in: `/anthropic/resources/beta/skills/skills.py`

**Main Operations:**
- `create()` - Upload and create a custom skill
- `retrieve()` - Get information about a specific skill
- `list()` - List available skills (custom or Anthropic-provided)
- `delete()` - Remove a custom skill
- `versions` - Manage skill versions

**Skill Creation:**
```python
client.beta.skills.create(
    display_title="My Custom Skill",
    files=[...],  # Must include SKILL.md at root
    betas=["skills-2025-10-02"]
)
```

#### B. Container System (`anthropic/types/beta/beta_container_params.py`)

**Container Structure:**
```python
class BetaContainerParams(TypedDict, total=False):
    id: Optional[str]  # Container identifier for reuse
    skills: Optional[Iterable[BetaSkillParams]]  # Skills to load
```

**Skill Parameters:**
```python
class BetaSkillParams(TypedDict, total=False):
    skill_id: Required[str]  # e.g., "pptx", "xlsx"
    type: Required[Literal["anthropic", "custom"]]  # Source type
    version: str  # Version or "latest"
```

#### C. Messages API Integration (`anthropic/resources/beta/messages/messages.py`)

The `container` parameter is passed to the messages API:

```python
response = client.beta.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    betas=["code-execution-2025-08-25", "skills-2025-10-02"],
    container={
        "skills": [
            {
                "type": "anthropic",
                "skill_id": "pptx",
                "version": "latest"
            }
        ]
    },
    messages=[...],
    tools=[...]  # Usually includes code_execution tool
)
```

### 3. **How It Works Under the Hood**

#### Request Flow:
1. **Client-Side Processing:**
   - The SDK validates the `container` parameter structure
   - Skill configurations are serialized into the request body
   - Beta headers are automatically added: `anthropic-beta: code-execution-2025-08-25,skills-2025-10-02`

2. **API Request:**
   ```python
   # In messages.py create() method:
   return self._post(
       "/v1/messages?beta=true",
       body=maybe_transform({
           "max_tokens": max_tokens,
           "messages": messages,
           "model": model,
           "container": container,  # Skills loaded here
           "tools": tools,
           # ... other params
       }, message_create_params.MessageCreateParams),
       # ...
   )
   ```

3. **Server-Side Processing (Inferred):**
   - Anthropic's API receives the container configuration
   - A sandboxed container environment is created/reused (based on `container.id`)
   - Requested skills are loaded into the container:
     - For `"anthropic"` type: Pre-built Anthropic skills are loaded
     - For `"custom"` type: User-uploaded skills are loaded
   - The skill files (Python modules, dependencies) become available in the execution environment
   - Code execution tools can import and use these skills

4. **Execution:**
   - Claude generates code that imports and uses the skill libraries
   - The `code_execution` tool runs the code in the container
   - Skills provide APIs/functions that Claude can call
   - Results are returned to Claude and back to the client

### 4. **Skill Structure**

When creating custom skills, files must include:
- **SKILL.md** - Required at root, describes the skill
- **Python modules** - The actual skill implementation
- **Dependencies** - Can be bundled or installed in container
- All files must be in the same top-level directory

### 5. **Container Lifecycle**

**Container Reuse:**
```python
# First request - creates container
response1 = client.beta.messages.create(
    container={"id": "my-container", "skills": [...]},
    # ...
)

# Subsequent requests - reuses same container
response2 = client.beta.messages.create(
    container={"id": "my-container"},  # Same ID
    # ...
)
```

Benefits:
- Faster execution (no skill reload)
- Persistent state across requests
- Shared filesystem/context

### 6. **Integration with Tools**

Skills typically work with the code execution tool:

```python
tools=[{
    "type": "code_execution_20250825",
    "name": "code_execution"
}]
```

Claude can:
1. Understand the task (e.g., "create a presentation")
2. Generate Python code that uses the skill
3. Execute the code via code_execution tool
4. Access skill APIs (e.g., `pptx` for PowerPoint)
5. Return results (e.g., generated file)

### 7. **Beta Version Management**

The SDK handles beta versioning:
```python
extra_headers = {
    "anthropic-beta": ",".join(chain(
        (str(e) for e in betas), 
        ["skills-2025-10-02"]
    ))
}
```

This ensures:
- The correct API version is called
- Skills feature is enabled
- Multiple beta features can coexist

## Example Anthropic Skills

Based on the example, Anthropic provides built-in skills like:
- **pptx** - PowerPoint/presentation creation
- **xlsx** - Excel/spreadsheet manipulation
- **docx** - Word document handling
- And potentially others

## Security & Sandboxing

- Skills run in isolated container environments
- Limited access to system resources
- Container can be destroyed after use or persisted
- Custom skills are uploaded and stored securely

## Key Files in SDK

1. **`/resources/beta/skills/skills.py`** - Skills CRUD operations
2. **`/resources/beta/messages/messages.py`** - Messages API with container support
3. **`/types/beta/beta_container_params.py`** - Container type definitions
4. **`/types/beta/beta_skill_params.py`** - Skill type definitions
5. **`/types/beta/message_create_params.py`** - Message creation parameters

## Summary

The agent skills feature provides a powerful way to extend Claude's capabilities through:
- **Pre-built Anthropic skills** for common tasks (documents, presentations, etc.)
- **Custom skills** you can upload
- **Container-based execution** for isolation and reusability
- **Seamless integration** with code execution and the Messages API
- **Version management** through beta flags

The SDK handles serialization, API communication, and beta version management, making it easy to use skills without dealing with low-level details.
