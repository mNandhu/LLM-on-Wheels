# Copilot Instructions & Best Practices

## General
1.  **Understand the Goal:** Before suggesting code, the assistant should ensure it understands the specific task or feature the user wants to implement. It should ask clarifying questions if needed.
2.  **Context is Key:** The assistant should pay close attention to the active file and relevant files like `#GraphAgent/core/graph.py`, `#GraphAgent/core/state.py`, and `#GraphAgent/core/nodes.py`. It should use the provided context to generate relevant suggestions.
3.  **Follow Requirements:** The assistant should adhere strictly to the requirements given in the prompt.
4.  **Code Clarity:** The assistant should generate clear, readable, and well-commented code. It should follow Python best practices (PEP 8).
5.  **Incremental Changes:** The assistant should suggest small, logical changes rather than large, complex refactors, unless specifically requested. It should explain the reasoning behind the changes.
6.  **Use Placeholders:** When unsure about specific variable names, API keys, or configurations, the assistant should use clear placeholders (e.g., `YOUR_API_KEY`) and indicate that they need to be replaced.
7.  **Error Handling:** The assistant should include basic error handling where appropriate (e.g., `try...except` blocks).
8.  **Dependencies:** If suggesting code that requires new libraries, the assistant should mention the necessary imports and installation commands (e.g., `pip install new-library`).
9.  **Testing:** The assistant should remind the user to test the generated code and offer to help generate unit tests if applicable.
10. **Security:** The assistant should avoid generating code that handles sensitive information (like passwords or API keys) insecurely and should not ask for sensitive information.
11. **Efficiency:** The assistant should consider potential performance implications, especially within graph execution nodes like those in `#GraphAgent/core/nodes.py`.

## LangGraph Specific
1.  **State Management:** When modifying the graph or nodes, the assistant should be mindful of the `#GraphAgent/core/state.py` definition and ensure state updates are consistent.
2.  **Node Logic:** The assistant should keep node functions (#GraphAgent/core/nodes.py) focused on their specific tasks within the graph.
3.  **Graph Structure:** The assistant should clearly explain changes to the graph definition in `#GraphAgent/core/graph.py`, including adding/removing nodes or edges.
4.  **Prompt Engineering:** When modifying prompts (like those imported in `#GraphAgent/core/nodes.py`), the assistant should explain the changes and their expected impact on the LLM's behavior.
5.  **Debugging:** The assistant should leverage the `debugMode=True` flag in `#GraphAgent/core/graph.py` or suggest adding logging/print statements for troubleshooting.

## Interaction
1.  **Be Concise:** The assistant should keep answers focused and to the point.
2.  **Use Markdown:** The assistant should format responses using Markdown, especially for code blocks (using 4 backticks and specifying the language).
3.  **File Paths:** The assistant should use `// filepath:` comments in code blocks when suggesting changes to specific files.
4.  **Package Management**: The assistant should use 'uv add <PackageName>' to add new packages to the project.
5. **Linting issues**: The assistant should check for linting issues in the code after implementing changes.