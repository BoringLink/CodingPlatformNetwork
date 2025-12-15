## 1. Project Overview and Goals

- **Core Objective**: Build an educational knowledge graph system using Neo4j as the graph database. The system processes student and teacher data records (interactions, courses, errors) via a small LLM (Aliyun Tongyi Qianwen) to classify and generate nodes/relationships. Provide interactive visualization with features like subviews based on filters, mouse hover for node details, node highlighting on click, and report generation.
- **Key Features**:
  - Node types: Student, Teacher, KnowledgePoint, Course, ErrorType.
  - Relationship types: CHAT_WITH, LIKES, TEACHES, LEARNS, CONTAINS, HAS_ERROR, RELATES_TO.
  - LLM integration for semantic analysis (e.g., error type identification, knowledge point extraction).
  - Backend: FastAPI for APIs, Celery for async tasks, Redis for caching.
  - Frontend: Next.js with Cytoscape.js for graph visualization, supporting filters, subviews, and interactions.
  - Support large-scale data (batch processing, rate limiting).
- **Non-Goals**: Avoid adding features outside the scope, such as multi-modal data (e.g., images/videos), advanced ML training, or external integrations unless explicitly in tasks.md.
- **Assumption**: All agents have access to the provided documents (tasks.md, requirements.md, design.md). Reference them explicitly in responses.

## 2. Development Principles

- **Code Style and Quality**:

  - Use type hints everywhere (strict mypy checks).
  - Follow PEP 8, but enforce via Ruff (no Black needed).
  - Structure code as per design.md: services (e.g., GraphManagementService), routers, models.
  - Keep functions small (<50 lines), modular, and testable.
  - Use async/await for I/O-bound operations (e.g., DB queries, LLM calls).
    Implement error handling: Global exceptions in FastAPI, retries (exponential backoff) for LLM/DB, logging with structlog.
    Coverage: Aim for >80% code coverage, 100% for API endpoints and properties.

- **Performance and Scalability**:

  - Batch operations: Limit to 1000 records/batch, use transactions.
  - Caching: LLM responses, query results in Redis (TTL-based expiration).
  - Queries: Optimize Cypher with indexes/constraints as in design.md.
  - Avoid blocking calls; use Celery for heavy tasks (e.g., imports, LLM batches).

- **Security Rules**:

  - No hardcoding secrets; use .env with pydantic-settings.
  - Validate all inputs (Pydantic), prevent injections (parameterized Cypher).
  - LLM: Sanitize prompts to avoid injection; anonymize sensitive data.
  - Auth: Implement JWT/RBAC for APIs (admin, teacher roles).
  - Logging: No sensitive data in logs; use structured format.
  - Before starting backend services or modifying backend dependencies, you must activate the virtual environment to avoid contaminating the global environment.

- **best practices**:
  - Technology Selection: Always prioritize the latest stable and optimal solutions, as verified through official sources (e.g., updated versions above). This ensures performance gains and security fixes, fostering a forward-thinking mindset that adapts to industry evolution—e.g., upgrading Python to 3.14 for its enhancements in error handling and speed.
  - Pre-Implementation Research: Before coding, consult the official documentation of the framework or library in use. This habit builds deeper understanding, reduces errors, and encourages self-reliance, turning routine tasks into learning opportunities.
  - Post-Implementation Testing: After completing any task, ensure comprehensive test coverage (unit, integration, E2E) and verify all tests pass before proceeding. This reinforces reliability, catches edge cases early, and cultivates a disciplined approach to quality, much like how thorough testing in real-world projects prevents costly downstream fixes.

## 3. Task Handling Rules

- **Prioritization**: Follow tasks.md strictly. Complete unchecked ([ ]) tasks in order, focusing on "\*" marked property tests first. Checked ([x]) tasks are done—do not revisit unless bugs are found.
- **Implementation Workflow**:
  1. **Analyze**: Reference requirements.md for user stories/acceptance criteria, design.md for interfaces/schemas.
  2. **Plan**: Outline steps, e.g., "Implement createNode in GraphManagementService, then test with PBT."
  3. **Code**: Generate code snippets in context (e.g., full functions/classes). Use arbitrary generators from design.md for PBT.
  4. **Test**: Every feature requires unit tests + property-based tests (using hypothesis). Cover edges (e.g., duplicates, failures). For frontend, test components/interactions.
  5. **Integrate**: Ensure changes fit architecture (e.g., add to Docker Compose if needed).
  6. **Document**: Update inline docs, API docs via FastAPI.
- **Property-Based Testing (PBT)**: Mandatory for all "\*" tasks in tasks.md. Use fc.assert(fc.property(...)) pattern from design.md examples. Run at least 100 iterations. Define arbitraries for realistic data (e.g., arbitraryNodeType).
- **Checkpoints**: At checkpoints (e.g., task 10,19,31), verify all prior tests pass. If issues, report: "Checkpoint failed: [details]. Suggest fixes?"
- **Frontend Specifics**:
  - Visualization: Use Cytoscape for rendering; map node types to colors/shapes.
  - Interactions: Hover for details (getNodeDetails), click to highlight neighbors.
  - Subviews: Store in Zustand; apply filters (time, type) to subgraph queries.
  - Responsive: Mobile-friendly with Tailwind.

## 4. Response Guidelines for Agents

- **Structure Responses**: Always use Markdown. Divide into sections: Analysis, Plan, Code (if applicable), Tests, Next Steps.
- **Conciseness**: Be rational, logical, and succinct. Use bullet points/lists for plans. Explain reasoning briefly.
- **Learning Focus**: In explanations, highlight best practices (e.g., "This uses Pydantic for validation to ensure type safety, improving code reliability.").
- **Research**: For tech questions, prioritize official docs (e.g., Neo4j docs, FastAPI guide). Use tools like browse_page if needed for latest info.
- **Refusals**: If task is out-of-scope (e.g., add unrelated feature), say: "This violates project rules [section]. Alternative: [suggestion]."
- **Collaboration**: If user input needed (e.g., bug clarification), ask targeted questions.
- **Updates**: Do not modify these rules. If evolution needed, propose in a separate section.

## 5. Testing and Quality Assurance

- **Types**:
  - Unit: Isolate components (e.g., service methods).
  - Integration: DB/LLM mocks; test full flows.
  - E2E: Playwright for UI flows (import -> visualize -> report).
  - Performance: Measure against metrics in design.md (e.g., <100ms queries).
- **Edges**: Test failures (e.g., LLM retry 3x), duplicates, large data.
- **Coverage**: Run reports; fix gaps.
- **CI/CD**: Assume GitHub Actions; code must pass lint/test before merge.

## 6. Deployment and Maintenance

- **Local**: Docker Compose for all services (Neo4j, Redis, Postgres if used, backend, frontend).
- **Production**: Kubernetes ready; use Caddy/Nginx proxy.
- **Monitoring**: Integrate Sentry for errors, Prometheus/Grafana for metrics.
- **Docs**: Generate API docs; write user/dev guides as per task 30.

Adhere to these rules to ensure the project delivers a robust, scalable education knowledge graph system that aids learning growth through structured insights and visualizations.
