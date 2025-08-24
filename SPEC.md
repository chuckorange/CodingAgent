# Claude‑Code MVP – Technical Specification (MVP v0.1)

## 1) Problem & Features

Develop a local coding agent  that can: understand a task, retrieve relevant repo context, propose minimal diffs, run/tests in a sandbox, and create a PR with a clean description.

**MVP features**

- Python Language 
- Understand the codebase (file tree, symbols, dependencies)
- Add small new features
- Fix bugs and failing tests
- Propose and apply code changes with explanations
- GitHub integration
- Sanbox for Run/Test/Verify
- Humman in the loop for permision

**Non‑goals :**
- User-defined agents 
- MCP integration
- Editor integration (VS Code/Cursor)

---

## 2) User Stories

### Core Workflows

1. **Explore codebase**: "devagent explore" → agent analyzes project structure, identifies key components, maps dependencies, explains architecture and data flow
2. **Understand specific code**: "devagent explain src/auth.py" → agent reads file, analyzes context, explains purpose, dependencies, and how it fits into overall system  
3. **Small feature**: "devagent add GET /users/\:id" → adds handler, updates router/types, adds/updates tests
4. **Fix failing tests**: "devagent fix tests" → agent finds failure, edits code/tests, passes locally, opens PR
5. **Explain change**: Show rationale + risks in PR and inline code comments for tricky edits

### Codebase Exploration Details

**Initial Project Discovery**: 
- "What does this codebase do?" → Overview of project purpose, main features, tech stack
- "How is this structured?" → Directory layout, module organization, key entry points
- "What are the main data models?" → Database schemas, core entities, relationships

**Architecture Understanding**:
- "Show me the request flow" → Trace HTTP requests through middleware, handlers, services  
- "How does authentication work?" → Map auth flow, identify security components
- "What external services does this use?" → API integrations, databases, message queues

**Development Context**:
- "Where should I add a new API endpoint?" → Suggest appropriate files and patterns
- "What testing patterns are used here?" → Identify test frameworks, conventions, coverage gaps
- "How do I run/deploy this?" → Find build scripts, deployment configs, development setup

---
## 3) System Overview

### 3.1 Components
- **Command (`devagent`)** – task entrypoint
- **Planner (LLM)** – produce structured work plan
- **Retriever** – search over codebase
- **Editor (LLM)** – output unified diffs; AST‑aware constraints where possible
- **Executor** – sandbox runner; test selection/execution
- **Verifier** – parse results; decide pass/fail and next actions
- **PR Bot** – creates PRs with title/body, attaches run logs, and adds inline review comments on risky hunks

### 3.2 Architecture
```mermaid
+---------------------+
| User / CLI          |
+----------+----------+
           |
           v
+----------+----------+
|  Supervisor          |
|  (route)             |
+----+-----+-----+-----+
     |     |     |
     |     |     +--------------------------+
     |     |                                |
     v     v                                v
 [Planner] [Retriever] ...           [Editor]
     |                                   |
     +--------> standard loop ---------->|
                                         v
                             [Policy] -> [Executor] -> [Verifier]
                                                | pass      | fail
                                                v           v
                                              [PR]     back to loop
```

### 3.3 Data Flow
1. **User input (CLI):** natural task string
2. **Planner:** uses repo summary to emit JSON plan `{steps[], files[], tests[]}`
3. **Retriever:** composes context pack: file snippets near symbols, build files, failing test output
4. **Editor:** generates *unified diff* only; agent applies patch with safe patcher (rejects bad hunks)
5. **Executor:** runs `prep → build → tests` inside Docker; captures outputs/coverage
6. **Verifier:** parses failures, updates state; triggers reflection (with retry budget N≤5)
7. **PR Bot:** creates PR with summary, changelog, test evidence, and TODOs
---

## 4) Architecture & Data Flow
1. **User input (CLI):** natural task string.
2. **Planner:** uses repo summary to emit JSON plan `{steps[], files[], tests[]}`.
3. **Retriever:** composes context pack: file snippets near symbols, build files, failing test output.
4. **Editor:** generates *unified diff* only; agent applies patch with safe patcher (rejects bad hunks).
5. **Executor:** runs `prep → build → tests` inside Docker; captures outputs/coverage.
6. **Verifier:** parses failures, updates state; triggers reflection (with retry budget N≤5).
7. **PR Bot:** creates PR with summary, changelog, test evidence, and TODOs.

### 4.1 Framework choices for a fast MVP

**Recommendation (Python‑first):** Use **LangGraph** for the agent state machine + **FastAPI** for a local API, with **OpenAI function‑calling (or Claude Tools)** as the LLM interface. This hits the right balance of control, debuggability, and speed.

#### Orchestration / Agent frameworks

- **LangGraph** – Graph/Machine abstraction with checkpoints, branches, retries. Great for explicit *Plan → Retrieve → Edit → Run → Verify* loops. Easy to persist state and instrument. *→ Recommended.*
- **AutoGen** – Multi‑agent chat patterns. Good for research; heavier for deterministic patch loops.
- **Semantic Kernel** – Strong C# interop; decent Python. Heavier setup; plugins good, graphing less explicit than LangGraph.
- **LlamaIndex** – Excellent retrieval pipelines; can pair with LangGraph (use as your Retriever) or use its Agent/Graph if you want a single toolkit.
- **Haystack** – Mature RAG pipelines, evaluators; more documents‑centric than code agents but solid retrieval.
- **OpenAI Assistants / Anthropic Tool‑Use** – Quick start for tool‑calling, but less control over deterministic loops and local state.

#### Retrieval & indexing

- **tree‑sitter** for symbols/AST; **ripgrep** for lexical search; **sentence‑transformers** (bge‑small or MiniLM) + **FAISS** for embeddings.
- **SQLite** to store file metadata, symbol map, and chunk→embedding ids (simple, portable).

#### Diffing & patch safety

- Generate **unified diff** in the LLM; apply with `git apply --3way --reject` and a custom hunk validator.
- Optional AST guard: **libcst** (Python) or **ts‑morph** (TypeScript) to sanity‑check edits before apply.

#### Execution sandbox

- **Docker** + Python base image (`python:3.11-slim`), pinned toolchain (`pytest`, `ruff`, `black`).
- Runner via **subprocess** inside container; cap time/CPU/mem.

#### Minimal stack (copy‑paste ready)

- Orchestration: **LangGraph**
- LLM client: **openai/anthropic** SDK (function calling / tool use)
- API: **FastAPI** (optional, for local HTTP endpoints)
- Retrieval: **ripgrep**, **tree‑sitter**, **sentence‑transformers + FAISS**, **SQLite**
- Patching: **gitpython** or shell `git`, plus custom validator
- Sandbox: **Docker SDK for Python** or shell `docker`
- PRs: **PyGitHub** (or GitHub App via REST)

#### Tiny LangGraph skeleton

```python
from langgraph import StateGraph, END
from typing import TypedDict, Literal

class AgentState(TypedDict):
    goal: str
    plan: dict
    context: str
    diff: str
    run_result: dict
    verdict: Literal["pass", "fail", "error"]
    iter: int
    current_step: str
    next_step: str
    error_msg: str

# Multi-agent supervisor architecture
g = StateGraph(AgentState)

# Agent implementations with proper state transitions
def supervisor_agent(state: AgentState) -> AgentState:
    """Routes to next agent based on current workflow state"""
    return state  # Pass through - routing handled by conditional edges

def planner_agent(state: AgentState) -> AgentState:
    """Creates execution plan and sets next step"""
    # LLM call to create plan using repo summary
    plan = create_plan(state["goal"])  # Implementation needed
    return {
        **state,
        "plan": plan,
        "next_step": "retrieve"
    }

def retriever_agent(state: AgentState) -> AgentState:
    """Gathers relevant context and sets next step"""
    # Use ripgrep, tree-sitter, vector search
    context = build_context(state["plan"])  # Implementation needed
    return {
        **state,
        "context": context,
        "next_step": "edit"
    }

def editor_agent(state: AgentState) -> AgentState:
    """Generates unified diff and sets next step"""
    # LLM call to generate diff
    diff = generate_diff(state["plan"], state["context"])  # Implementation needed
    return {
        **state,
        "diff": diff,
        "next_step": "execute"
    }

def executor_agent(state: AgentState) -> AgentState:
    """Runs tests in sandbox and sets next step"""
    # Apply diff and run tests in Docker
    result = run_tests_in_sandbox(state["diff"])  # Implementation needed
    return {
        **state,
        "run_result": result,
        "next_step": "verify"
    }

def verifier_agent(state: AgentState) -> AgentState:
    """Analyzes results and determines next action"""
    # Parse test results to verdict
    verdict, error_msg = parse_test_results(state["run_result"])
    
    if verdict == "pass":
        next_step = "pr"
    elif state.get("iter", 0) >= 5:
        next_step = "end"
    else:
        next_step = "reflect"
    
    return {
        **state,
        "verdict": verdict,
        "error_msg": error_msg,
        "next_step": next_step
    }

def reflector_agent(state: AgentState) -> AgentState:
    """Reflects on failure and updates plan"""
    # LLM call to analyze failure and update plan
    updated_plan = reflect_and_replan(state["plan"], state["error_msg"])
    return {
        **state,
        "plan": updated_plan,
        "iter": state.get("iter", 0) + 1,
        "next_step": "retrieve"
    }

def pr_agent(state: AgentState) -> AgentState:
    """Creates PR and ends workflow"""
    # Create GitHub PR
    pr_url = create_github_pr(state["diff"], state["plan"])
    return {
        **state,
        "pr_url": pr_url,
        "next_step": "end"
    }

# Add all nodes
g.add_node("supervisor", supervisor_agent)
g.add_node("planner", planner_agent)
g.add_node("retriever", retriever_agent)
g.add_node("editor", editor_agent)
g.add_node("executor", executor_agent)
g.add_node("verifier", verifier_agent)
g.add_node("reflector", reflector_agent)
g.add_node("pr_agent", pr_agent)

# Supervisor routing logic
def supervisor_router(state: AgentState) -> str:
    next_step = state.get("next_step", "plan")
    
    if next_step == "plan":
        return "planner"
    elif next_step == "retrieve":
        return "retriever"
    elif next_step == "edit":
        return "editor"
    elif next_step == "execute":
        return "executor"
    elif next_step == "verify":
        return "verifier"
    elif next_step == "reflect":
        return "reflector"
    elif next_step == "pr":
        return "pr_agent"
    else:  # next_step == "end"
        return END

# Connect nodes - all agents return to supervisor for routing
g.add_conditional_edges("supervisor", supervisor_router)
for agent in ["planner", "retriever", "editor", "executor", "verifier", "reflector"]:
    g.add_edge(agent, "supervisor")
g.add_edge("pr_agent", END)

g.set_entry_point("supervisor")
engine = g.compile()
```

---

## 5) Evaluation Framework

### 5.1 Success Metrics (Automated)

**Task Completion Metrics**
- **End-to-End Success Rate**: % of tasks completed from plan to PR without human intervention
- **Test Pass Rate**: % of generated code that passes existing test suites
- **Build Success Rate**: % of changes that compile/build without errors
- **Patch Apply Rate**: % of generated unified diffs that apply cleanly with `git apply`

**Quality Metrics**
- **Code Quality Scores**: Static analysis metrics (cyclomatic complexity, maintainability index)
- **Diff Minimality**: `lines_changed / functionality_points` ratio
- **Test Coverage**: % of new code covered by tests (existing + agent-generated)
- **Convention Adherence**: % compliance with linting rules (ruff, black, etc.)

**Performance Metrics**
- **Task Completion Time**: Average time from user input to PR creation
- **Iteration Count**: Average retry cycles needed per successful task
- **Context Efficiency**: Tokens used vs. task complexity

### 5.2 Human Evaluation

**Code Review Quality (1-5 Likert Scale)**
- **Readability**: Code clarity and documentation quality
- **Correctness**: Logic accuracy and edge case handling  
- **Maintainability**: Future-proofing and extensibility
- **Security**: Absence of vulnerabilities and best practices

**PR Quality Assessment**
- **Description Clarity**: How well PR explains rationale and changes
- **Reviewer Burden**: Average comments/change requests per PR
- **Merge Acceptance Rate**: % of PRs merged without major revisions
- **Time to Merge**: Hours from PR creation to merge

### 5.3 Benchmark Datasets

#### 5.3.1 Synthetic Test Repository

**Repository Structure:**
```
devagent-bench/
├── simple-flask-api/     # REST API with SQLite
├── data-pipeline/        # ETL scripts with pandas
├── cli-tool/            # Click-based command line app
└── microservice/        # FastAPI + PostgreSQL service
```

**Task Categories by Complexity:**

**Level 1: Simple Tasks (baseline)**
- Add new REST endpoint with validation
- Fix obvious bug (missing import, typo)
- Add unit test for existing function
- Update dependency version in requirements.txt

**Level 2: Medium Tasks**
- Implement new business logic with database changes
- Refactor function to improve performance
- Add error handling and logging
- Fix failing integration test

**Level 3: Complex Tasks**
- Design and implement new feature across multiple files
- Debug race condition or concurrency issue
- Optimize database queries and add indexes
- Implement authentication/authorization

#### 5.3.2 Real-World Task Dataset

**Open Source Repository Tasks:**
- Collect issues labeled "good first issue" from popular Python repos
- Create reproducible task descriptions with success criteria
- Maintain ground truth solutions from actual merged PRs

**Task Examples:**
```yaml
task_001:
  description: "Add user profile endpoint to Flask API"
  repo: "simple-flask-api"
  files_expected: ["app.py", "models.py", "test_users.py"]
  success_criteria:
    - GET /users/:id returns user data
    - Handles 404 for missing users
    - Includes input validation
    - Has unit tests with >90% coverage
```

### 5.4 Evaluation Pipeline

#### 5.4.1 Automated Testing

**Pre-commit Evaluation:**
```python
def evaluate_agent_pr(pr_diff, base_repo):
    metrics = {}
    
    # Apply diff and run tests
    metrics['patch_applies'] = apply_diff_safe(pr_diff, base_repo)
    metrics['tests_pass'] = run_test_suite(base_repo)
    metrics['builds'] = run_build_command(base_repo)
    
    # Static analysis
    metrics['lint_score'] = run_linter(base_repo)
    metrics['complexity'] = calculate_complexity(pr_diff)
    
    # Coverage analysis
    metrics['coverage_delta'] = measure_coverage_change(pr_diff)
    
    return metrics
```

**Benchmark Runner:**
```bash
# Run evaluation suite
devagent-eval --dataset=benchmark-v1.0 --agent=devagent --output=results.json

# Generate report
devagent-eval report --results=results.json --format=html
```

#### 5.4.2 Human Review Process

**Review Protocol:**
1. **Blind Review**: Reviewers don't know if code is human or agent-generated
2. **Standardized Rubric**: 5-point scale across readability, correctness, maintainability
3. **Multiple Reviewers**: At least 2 reviewers per task for inter-rater reliability
4. **Feedback Collection**: Specific comments on what could be improved

**Reviewer Pool:**
- Senior engineers (3+ years experience)
- Domain experts for specific task types
- Mix of internal team + external contractors

### 5.5 Success Thresholds (MVP Targets)

**MVP Acceptance Criteria:**
- **Task Completion Rate**: >70% for Level 1 tasks, >40% for Level 2
- **Test Pass Rate**: >90% (should not break existing functionality)
- **Human Review Score**: >3.5/5.0 average across all dimensions
- **Patch Apply Rate**: >95% (diffs must be syntactically correct)

**Production Readiness Targets:**
- **Task Completion Rate**: >90% for Level 1, >70% for Level 2, >30% for Level 3
- **Security Score**: 0 critical vulnerabilities introduced
- **Performance**: <10% regression in runtime/memory for modified code
- **Developer Satisfaction**: >4.0/5.0 in usability surveys

### 5.6 Continuous Evaluation

**Production Monitoring:**
- Track success rates on real developer tasks
- Monitor post-deployment bug rates for agent-generated code
- Collect developer feedback through in-CLI surveys
- A/B testing: agent vs. manual coding for similar tasks

**Model Improvement Loop:**
- Use failed tasks to create additional training examples
- Analyze common failure patterns to improve prompts
- Regularly update benchmark datasets with new task types
- Version control evaluation results to track progress over time

---

## Appendix: Alternative Stacks & Trade‑offs

### Orchestration / Agents

| Option                       | Strengths                                             | Weaknesses                                           | Use when                                           |
| ---------------------------- | ----------------------------------------------------- | ---------------------------------------------------- | -------------------------------------------------- |
| **Plain Python loop**        | Fastest to start, zero deps, total control            | No built‑ins for retries/branches/checkpointing      | POC in 1–2 days; you'll add LangGraph later        |
| **LangGraph**                | Deterministic graphs, state checkpoints, good tooling | Another dep; learning curve                          | You want reliability + observability from week 1   |
| **OpenAI Assistants**        | Quick tool‑use, hosted memory, eval UI                | Less control over state; vendor‑lock; harder offline | Hack together quickly without custom orchestration |
| **Anthropic Tool‑Use**       | Strong model reasoning, simple tool calls             | Fewer orchestration primitives                       | You stay Anthropic‑only and want simplicity        |
| **AutoGen**                  | Multi‑agent patterns, rich examples                   | Chatty, more complex, nondeterministic               | Researching agent roles; not strict patch loops    |
| **LlamaIndex (Agent/Graph)** | Integrated RAG + agents, observability                | Heavier; opinionated                                 | You want a one‑stop data+agent toolkit             |
| **Semantic Kernel**          | Plugins, planners, C# first                           | Python less mature; graphing weaker                  | .NET shop, VS/Windows integration                  |
| **Haystack Agents**          | Solid RAG, evaluators                                 | Docs‑centric, limited code‑agent patterns            | Strong doc RAG + light agent needs                 |

### Retrieval / Indexing

| Option                              | Strengths                                  | Weaknesses                               | Use when                                        |
| ----------------------------------- | ------------------------------------------ | ---------------------------------------- | ----------------------------------------------- |
| **ripgrep + tree‑sitter + SQLite**  | Local‑first, simple, fast, great precision | DIY ranking, ops on you                  | MVP with tight control, no external services    |
| **LlamaIndex vector + graph**       | Many loaders, composable retrievers        | Extra complexity; cost if hosted         | Want advanced retrieval quickly                 |
| **Haystack (Elasticsearch/Qdrant)** | Production RAG plumbing                    | Service to run; tuning                   | You already have ES/Qdrant and ops              |
| **FAISS (local)**                   | Zero‑server, fast ANN                      | In‑memory unless you persist; no filters | Single‑repo, small/medium codebases             |
| **Qdrant/Weaviate/pgvector**        | Filters, persistence, scale                | Another service to operate               | Multi‑repo, team‑wide code memory               |
| **Sourcegraph src‑cli**             | Best‑in‑class code search                  | External dependency                      | Enterprise repos; avoid writing your own search |

### Patch / Editing Strategy

| Strategy                                        | Strengths                               | Weaknesses                                | Use when                                  |
| ----------------------------------------------- | --------------------------------------- | ----------------------------------------- | ----------------------------------------- |
| **LLM unified diff**                            | Minimal changes, reviewable, git‑native | Can drift/patch‑fail; needs validator     | Default for small fixes/features          |
| **AST code‑mods (libcst/ts‑morph/jscodeshift)** | Structurally safe, repeatable           | Harder prompts; limited for creative code | Bulk mech changes, refactors, API renames |
| **LSP text edits**                              | Position‑accurate, language‑aware       | Implementing LSP infra is heavier         | Editor‑integrated fine‑grained edits      |

### Execution / Sandbox

| Option                  | Strengths                    | Weaknesses                        | Use when                    |
| ----------------------- | ---------------------------- | --------------------------------- | --------------------------- |
| **Local subprocess**    | Fast, zero infra             | Pollutes env; non‑reproducible    | Hackiest MVP on your laptop |
| **Docker/Podman**       | Reproducible, safe, portable | Startup overhead                  | Default for MVP + CI parity |
| **Nix**                 | Reproducible dev envs        | Learning curve; slower first‑time | Teams already on Nix        |
| **Firecracker/microVM** | Strong isolation             |                                   |                             |

