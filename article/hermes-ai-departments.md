# Building My Own AI Team with Hermes Agent

*How I’m combining local models, coding agents, and project memory for everyday work.*

AI tools can generate code, draft articles, and help produce video. As a developer, I wanted to bring those capabilities into a consistent workflow for building products and creating content.

I had the tools, but I was still coordinating everything: moving context between conversations, tracking decisions, and deciding what happened next. I chose Hermes Agent because its approach to memory and reusable skills offered a foundation for continuity across tasks. Whether that improves my results over time is something I still need to measure.

I started with three needs: developing my tennis app, Practice Partner; writing technical articles; and preparing video content. The result is a personal AI team organized around workflows, with clear records and deliberate handoffs.

## Organize the work around tasks

My first setup used separate planner, developer, QA, and reviewer profiles. That created more coordination than I needed for a personal project.

I replaced those profiles with departments. Each department coordinates a complete workflow; specialist sessions handle individual stages when needed. Requirements, decisions, checks, and the next action stay linked to the task.

![Role-based and task-centered coordination of the same development lifecycle. Specialist sessions remain useful for implementation, verification and review.](../diagrams/png/roles-vs-tasks.png)

*The same lifecycle, with continuity attached to the work.*

For software, the lifecycle is **Define → Design → Build → Verify → Review → Release → Learn**. I approve the specification before implementation and review the evidence before merging or releasing. Verification uses a separate session and the submitted commit; a different model alone does not guarantee an independent assessment.

## Four departments, shared principles

Each department is a Hermes Agent profile with reusable workflow instructions. Project-specific requirements belong in project records.

- **Development (`development-dept`):** software, websites, and mobile apps—from requirements to verified changes.
- **Writing (`writing-dept`):** articles, newsletters, and social posts—from brief to source checking and editorial approval.
- **Media (`media-dept`):** videos and short videos—from script to assets, production, and export review.
- **Dream Department (`discovery-dept`):** new ideas—from capture and clarification to evaluation, validation, and a decision.

Discovery helps me decide where to invest time. An approved idea becomes a planning brief for the relevant department. Existing bugs and approved work can enter Development directly.

## How the tools fit together

Hermes Agent is the coordinator: it reads the board, prepares plans, and communicates with me. Claude Code, Codex, and the optional OpenCode worker are execution tools. Selecting a coordinator model does not connect a coding worker.

![Complete tool map with Hermes Agent, Discord, Slack, ChatGPT, Codex, LM Studio, Qwen, Obsidian, Orca and Orca Mobile, Claude Code, OpenCode, Medium, Substack and X. Current tools and planned integrations are distinguished.](../diagrams/png/AI_Team_Tools_Architecture.png)

*Solid boxes identify current tools or configured services. Dashed boxes identify planned integrations; availability is not proof of an end-to-end workflow.*

At my desk, I use the Hermes Agent desktop app. Discord provides access to department conversations when I am away; Slack is also connected to the gateway. Orca Mobile provides remote access to Orca. My Mac stays awake to host the gateway and local model server.

ChatGPT remains a separate workspace for discussion and editing. Medium, Substack, and X are content destinations. Automated publishing and video production are not connected yet.

## Obsidian preserves the project context

I use a dedicated Obsidian vault for project requirements, plans, architecture notes, discussions, and decisions. **Kanban tracks what happens next; Obsidian records what we agreed and why.**

Discussion notes stay separate from approved specifications. Before a coding session, I provide the relevant documents and identify the specification revision it should follow. The task card links to that revision, along with the branch, commit, and verification results.

This is durable document memory. Automatic vault access and synchronization have not been verified.

## Choose models for the task

Development uses Codex as its coordinator, with local Qwen as a fallback. Writing, Media, and Discovery use local Qwen through LM Studio. These are workflow choices, not benchmark conclusions.

My planned combinations are:

- **New idea:** local Qwen captures and clarifies it. I request a Codex feasibility review when a specific engineering decision needs deeper analysis, then decide whether to proceed.
- **App feature:** Codex prepares the specification; Claude Code or Codex implements the approved scope in an Orca worktree; a separate session verifies the submitted commit.
- **Technical article:** local Qwen helps outline and draft. A separate review checks important claims against sources and configuration. I approve the final platform version before publication.
- **Article to video:** local Qwen prepares the script, scene list, and captions. Media tools must then produce an export that I watch and approve.
- **Small local coding task:** OpenCode with LM Studio is an option to test for repository analysis, documentation, and limited changes. Its provider connection, permissions, and tool calling still need validation.

Only one worker writes to a task’s worktree at a time. A worker change requires a recorded handoff: repository, branch, commit, unfinished work, check results, and next action.

An expired cloud model caused an early Discord request to fail, which led me to configure a local fallback. Fallback can support permitted summaries and draft preparation; it does not approve a new worker or substitute for executed tests. End-to-end failover remains untested.

## A minimal configuration to start

Start with the [Hermes Agent quickstart](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart/) and check the installed version. Back up existing configuration before merging examples.

**1. Create the department profiles.**

    hermes profile create development-dept
    hermes profile create writing-dept
    hermes profile create media-dept
    hermes profile create discovery-dept

Set each profile’s model through `hermes -p PROFILE_NAME model`. Use the supported sign-in flow for subscription access; a ChatGPT subscription is not a general-purpose API key.

**2. Serve a local model.** Load a suitable tool-capable model in LM Studio, start its server on port 1234, and check the available model IDs:

    curl http://127.0.0.1:1234/v1/models

Use the exact ID for the model you load. My configured ID is `qwen/qwen3.6-35b-a3b`, with endpoint `http://127.0.0.1:1234/v1`. Keep the server bound to loopback. Local inference does not make Discord messages or cloud reviews local.

**3. Keep dispatch disabled while testing.** Apply this block in the department configurations and the default gateway configuration, then restart the gateway:

    kanban:
      dispatch_in_gateway: false
      dispatch_profiles: []

This disables automatic Kanban dispatch. It is not a complete execution permission boundary; worker and publishing integrations need their own controls.

**4. Connect records and channels.** Create project boards, add workflow instructions to each profile’s `SOUL.md`, and route Discord channels to departments using the [Discord guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord). Keep bot credentials outside shared examples. Link each task to its approved Obsidian documents.

**5. Test one operation at a time.** Read the named board without changes, create one planning card, and read it back. Verify model tool calls and fallback separately before connecting a worker. The reference pack contains fuller configuration examples, workflow templates, and an OpenCode trial checklist.

## What works, and what comes next

All four department profiles are configured. Through Discord, I have tested Development reading the Tennis board and Discovery reading `idea-pipeline`, creating an idea card, and reading it back. The idea was a real-estate house-tour scheduling app; the response captured the problem and questions that need validation.

Local inference through LM Studio and Orca Mobile access are working. These checks establish a coordination foundation, not a complete autonomous development or publishing pipeline. A read-only Discovery request also renamed the channel, so that side effect still needs investigation.

My next steps are:

- Evaluate and validate the captured idea, then test an approved transfer to a linked planning card.
- Bind one Development task to the correct repository and Orca worker.
- Run that task through implementation, executed verification, and review of a fixed commit.
- Test local fallback and the OpenCode analysis configuration independently.
- Connect research, media production, and publishing one capability at a time.

I retain approval over worker dispatch, merge, release, and publication. Those decisions must refer to the exact specification, commit, draft, or export; automated enforcement still needs to be implemented.

The value so far is continuity: a place for each request, a record of decisions, and a clear next step. I will expand the system as each workflow passes a small, observable test.
