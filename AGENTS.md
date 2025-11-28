# AI Agent Instructions for MoLiM Project

## Issue Tracking with Beads

This project uses **Beads** (`bd`) for issue tracking and task management. All agents working on this project should use `bd` instead of markdown TODO lists or inline comments for tracking work.

### Quick Start

Before starting any work session:
```bash
bd ready --json  # Check for ready work
bd info          # Check database status
```

### Core Workflow

1. **Find Work**: Use `bd ready` to see issues with no blockers
2. **Create Issues**: File bugs, tasks, and improvements as you discover them
3. **Update Status**: Keep issue status current (`open`, `in_progress`, `closed`)
4. **Link Dependencies**: Use `bd dep add` to track blockers and relationships
5. **Sync**: Database auto-syncs via git hooks (pre-commit, post-merge)

### Creating Issues

```bash
# File bugs as you discover them
bd create "Fix invalid escape sequences in myFolders.py" -t bug -p 1 -l "phase1,quick-win"

# Track refactoring tasks
bd create "Migrate to SQLite database" -t task -p 1 -l "phase2,database"

# Epic for large features
bd create "Implement Tkinter GUI" -t epic -p 2 -l "phase5,gui"

# Link discovered work to parent
bd dep add <new-issue-id> <parent-issue-id> --type discovered-from
```

### Priority Levels
- **P0** (0): Critical bugs, blocking issues
- **P1** (1): High priority features/fixes
- **P2** (2): Medium priority (default)
- **P3** (3): Low priority
- **P4** (4): Nice-to-have

### Common Labels
Use labels for organization:
- `phase1`, `phase2`, `phase3`, `phase4`, `phase5`, `phase6` - Refactoring phases
- `quick-win` - Tasks completable in 1-2 days
- `database` - Database-related work
- `gui` - Tkinter GUI work
- `bug` - Bug fixes
- `refactoring` - Code improvement
- `documentation` - Docs updates

### Session End Protocol

Before ending any work session:

1. **File remaining work**: Create issues for any TODOs, bugs discovered, or follow-up tasks
2. **Update status**: Close completed issues, update in-progress work
3. **Sync database**: 
   ```bash
   bd sync              # Manual sync (usually automatic via hooks)
   git add .beads/      # Stage beads changes
   git commit -m "Update issue tracking"
   git push
   ```
4. **Verify clean state**: 
   ```bash
   bd info              # Check for uncommitted issues
   git status           # Verify all changes committed
   ```

### Querying Issues

```bash
# Ready work
bd ready --priority 1 --json

# Blocked issues
bd blocked

# Filter by labels
bd list --label phase1,quick-win

# View dependency tree
bd dep tree <issue-id>

# Search
bd list --title-contains "database"
bd list --status open --priority-min 0 --priority-max 1
```

### MoLiM Project Context

This is a **Movie Library Manager** that:
- Manages physical movie collections in folders
- Fetches IMDb metadata using cinemagoer
- Organizes by ratings (underscore prefix system)
- Generates statistics by directors/actors/genres

**Current Status**: Recently completed deep codebase analysis. Ready to begin **Phase 1: Foundation & Cleanup** refactoring.

**Key Documentation**:
- `OVERVIEW.md` - Complete architecture analysis
- `REFACTORING_PLAN.md` - 6-phase implementation roadmap
- `QUICK_START.md` - TL;DR with quick wins

### Using Beads with Refactoring Phases

The refactoring plan has 6 phases. When working on tasks, always tag with the appropriate phase:

```bash
# Phase 1: Foundation & Cleanup (Weeks 1-2)
bd create "Fix escape sequences" -t task -p 1 -l "phase1,quick-win"
bd create "Create config.yaml system" -t task -p 1 -l "phase1,configuration"

# Phase 2: Data Layer (Weeks 3-4)
bd create "Design SQLite schema" -t task -p 1 -l "phase2,database"
bd create "Implement Repository pattern" -t task -p 1 -l "phase2,database"

# Phase 3: Business Logic (Weeks 5-6)
bd create "Extract service layer" -t task -p 2 -l "phase3,refactoring"

# Phase 4: CLI (Weeks 7-8)
bd create "Implement Click CLI" -t task -p 2 -l "phase4,cli"

# Phase 5: Tkinter GUI (Weeks 9-10)
bd create "Design main window" -t task -p 2 -l "phase5,gui"

# Phase 6: Testing (Weeks 11-12)
bd create "Add unit tests for repositories" -t task -p 2 -l "phase6,testing"
```

### Dependencies

Use dependency types appropriately:
- `blocks` - Hard blocker (most common)
- `related` - Soft relationship
- `parent-child` - Hierarchical (epic → tasks)
- `discovered-from` - Work found during another task

Example:
```bash
# Task blocks another task
bd dep add bd-f14c bd-a1b2 --type blocks

# Epic with children
bd create "Database Migration" -t epic -p 1
# Children auto-assigned as bd-a1b2.1, bd-a1b2.2, etc.
```

### Tips for AI Agents

1. **File issues proactively**: Don't wait until session end
2. **Keep descriptions clear**: Include file paths and specific details
3. **Use JSON output**: `--json` flag for programmatic integration
4. **Check ready work first**: Always start with `bd ready`
5. **Link related work**: Use dependencies to maintain context
6. **Don't lose work**: If you notice something, file an issue immediately

### Resources

- Beads Documentation: https://github.com/steveyegge/beads
- Quick reference: `bd help`
- Interactive guide: `bd quickstart`
