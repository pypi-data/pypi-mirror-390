---
description: Begin work on a specific task from project board
---

Load context for task $ARGUMENTS from GitHub issue, create feature branch, and mark as "In Progress" on project board.

## Task Context Loading

1. **Read GitHub Issue**: 
   ```bash
   gh issue view $ARGUMENTS --json title,body,labels,state,assignees
   ```

2. **Load Plan Reference**:
   - Read relevant section from `docs/pyplanhat/PLAN.md`
   - Check task dependencies and prerequisites
   - Review completion criteria for the task

3. **Research Requirements**:
   - Check if task requires API research (P0-0)
   - Load any existing research from `docs/pyplanhat/RESEARCH.md`
   - Identify external documentation needed

## Branch Creation

Create feature branch following naming convention:
```bash
git checkout -b feature/$ARGUMENTS-task-name
```

## Project Board Update

Move task to "In Progress" on project board:
```bash
gh project item-edit <project-id> --field "Status" --value "In Progress" --issue $ARGUMENTS
```

## Context Summary

Provide a comprehensive context summary including:

### Task Details
- **Task ID**: $ARGUMENTS
- **Title**: [from GitHub issue]
- **Description**: [key requirements from issue body]
- **Dependencies**: [any prerequisite tasks]
- **Labels**: [relevant phase and priority]

### Implementation Plan
- **Phase**: [which phase this belongs to]
- **Key Requirements**: [specific deliverables]
- **Architecture Considerations**: [relevant patterns to follow]
- **Testing Requirements**: [what needs to be tested]

### Next Steps
- **Research Needed**: [if any API/docs research required]
- **Files to Create/Modify**: [specific file paths]
- **Quality Gates**: [completion criteria]
- **Dependencies**: [what must be completed first]

## Usage Examples

```bash
/start-task P0-1
# Loads context for P0-1, creates branch, begins work

/start-task P1-2
# Loads context for P1-2, checks P1 dependencies
```

## Agent Workflow

After running this command:
1. **Stay in current agent** to review context
2. **Switch to builder** (Tab key) to begin implementation
3. **Switch to reviewer** after implementation for quality check

## Notes

- Task IDs follow format: P{phase}-{task-number} (e.g., P0-1, P1-2)
- Users control agent switching manually via Tab key