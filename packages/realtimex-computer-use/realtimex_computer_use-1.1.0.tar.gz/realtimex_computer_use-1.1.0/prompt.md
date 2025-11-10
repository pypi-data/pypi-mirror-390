# Prompt 1:
I'm building an AI agent that automates tasks on a user's computer using deterministic steps to handle everyday workflows. I plan to build MCP Server(s) that provide computer-related tools so the agent can control and interact with the user's desktop and browser to complete tasks.

System design vision:
- Create a suite of specialized AI agents that each handle a distinct business workflow.
  Examples: a social-insurance agent that delegates to sub-tasks; an uploader agent that uploads downloaded invoices; a downloader agent that retrieves invoices, etc.
- Equip agents with tools to:
  1) Open web browsers,
  2) Fetching configured credentials (only return credential's names),
  3) control the browser via a PyAutoGUI MCP Server (already implemented),
  4) read and reference documentation. The system prompt will guide agents to consult the correct docs (already implemented).

Goal:
Conduct a comprehensive review to fully understand the task requirements. This phase will establish the foundational design for implementing the workflows.

Deliverable:
After reviewing the provided files, produce a thorough summary of your understanding to confirm alignment before we proceed with the dedicated implementation tasks.

# Prompt 2:
I confirm that the `realtimex-docs` MCP server has already been implemented and is located in a different folder. The code in the `examples` folder is provided for reference only and should not be considered as implementation evidence. Our next goal is to build a production-ready MCP server capable of interacting with the computer, which can be reused by any agents responsible for controlling the user's computer.

Our immediate task is to build this MCP server from scratch using FastMCP, exposing a tool that allows agents to open browser instances.

**Implementation Requirements:**
- Transport: MCP server communicates over stdio.
- Packaging: Use uv for dependency and project management; support distribution via uv and PyPI.
- Code Quality: Clean, well-structured, and pattern-aligned with MCP best practices.
- Naming: The package name MUST start with "realtimex-". Choose a concise, descriptive suffix.

**:Usage Expectation:**
Clients should be able to load the server on any machine running the agent with:
  uvx realtimex-<package-name>

**References (for patterns only)**
- Existing PyAutoGUI MCP server implementation (cloned from the public repo).
- FastMCP examples/snippets, including fastmcp_quickstart.py (from the MCP documentation).

**Development Philosophy**
- Ship production-ready, readable code that can land in main without follow-up fixes.
- Implement only what’s necessary; avoid over-engineering and opportunistic refactors.
- Prefer self-documenting code; add comments only to clarify intent or non-obvious decisions.

**Deliverable
A FastMCP-based MCP server meeting the above requirements that enables Agents to open browser(s).

# Prompt 3:
I think I’ll go with solution 2, 3, or another suitable approach, since saving and referencing images for detection is too costly at this stage. I plan to continue using existing tools like `get_screen_size` and `move_mouse(x, y)`, and possibly add new ones as needed. After that, I’ll update the prompt to guide the agent in using the correct tool sequence to calculate coordinates before executing `move_mouse(x, y)`. You can refer to the existing PyAutoGUI implementation in "examples/realtimex_pyautogui_server/server.py" for reference.

Finally, please propose the best design approach for this. I’ll review it and proceed with the implementation.

# Prompt 4:
Great work




