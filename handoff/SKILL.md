---
name: handoff
description: Create a HANDOFF.md file that captures the full state of the current work session so the next Claude (or human) can resume without losing context. Use this skill whenever the user asks to "hand off", "인계", "pass the baton", "save context", "write a handoff", invokes a `/handoff` command, or otherwise explicitly signals they want to wrap up the session and prepare a transition document. Do NOT trigger this proactively just because the session feels long — only when the user asks for it.
---

# Handoff

Capture everything a fresh agent needs to pick up where this session left off — in one self-contained `HANDOFF.md` at the repo root (or workspace root).

The goal is **resumability**, not a chat transcript. A reader who has never seen this conversation should be able to read the file, run a few commands, and continue the work confidently.

## When this skill is active

- The user has explicitly asked for a handoff. Don't second-guess them, but if their request is ambiguous ("wrap this up"), confirm they want a handoff document specifically.
- If a `HANDOFF.md` already exists at the target location, ask whether to overwrite, append a new section, or write to a different filename (`HANDOFF-2.md`, `HANDOFF-<topic>.md`). Default suggestion: overwrite if it's stale (>1 day old or clearly from an unrelated task), otherwise append.

## What to capture

Fill in every section below. If a section genuinely doesn't apply, write "N/A" with a one-line reason rather than dropping it — the next agent should never wonder if you forgot.

Pull facts from the actual session, not assumptions:
- File paths: from `view`, `bash_tool` outputs, or files you edited. Always absolute or repo-relative.
- Commands: ones that were actually run, not ones that "should" work. Mark untested commands clearly.
- Decisions: things the user explicitly chose or rejected, with one-line rationale.
- Open questions: anything you flagged for the user but didn't resolve.

## Output template

Write the file to the repo root unless the user specifies otherwise. Use this exact structure:

```markdown
# Handoff: <one-line task description>

**Date**: <YYYY-MM-DD>
**Session goal**: <what the user originally wanted to accomplish>
**Status**: <not started | in progress (X%) | blocked | mostly done | ready for review>

## TL;DR for the next agent

<3–5 sentences. What is this task, what's done, what's the single most important thing to do next.>

## Current state

### What's done
- <concrete completed items, with file paths>

### What's in progress
- <items partially done — name the file, what's there, what's missing>

### What's not started
- <known remaining work>

## Next steps

Ordered, concrete actions. Each should be doable without re-deriving context.

1. <action> — <file:line if applicable> — <expected outcome>
2. ...

## Blockers & open questions

Things that need a human decision or external input before the next agent can proceed.

- **<topic>**: <what's blocked, what decision is needed, options considered>

## Key files & locations

| Path | Purpose | Status |
|------|---------|--------|
| `path/to/file` | <what it does> | <new / modified / referenced> |

## Important code locations

- `path/to/file.ext:LINE` — <what's there and why it matters>

## Environment & setup

- **Runtime**: <node 20 / python 3.11 / etc.>
- **Key dependencies**: <only the non-obvious ones>
- **Setup commands**: <only if non-standard>
- **Env vars / secrets needed**: <names only, never values>

## Commands that work

Commands actually verified during this session:

```bash
# <what this does>
<command>
```

## Decisions made (and why)

- **<decision>**: <one-line rationale, who made the call>
- **Rejected: <alternative>** — <why not>

## Gotchas & landmines

Non-obvious things that bit us or will bite the next agent:

- <thing> — <why it matters>

## Conversation references

If specific past exchanges matter, summarize them — don't quote walls of chat.

- The user clarified that <X> means <Y>
- We tried <approach Z> and rolled it back because <reason>

## Files attached / created this session

- `path/to/file` — created
- `path/to/other` — modified
```

## Writing principles

**Density over completeness.** A 200-line handoff that's all signal beats a 1000-line dump. If something is obvious from looking at the code, don't restate it — point to the file.

**No flattery, no narration.** Skip "we had a great session exploring..." Just facts. The next agent doesn't need to know how the conversation felt.

**Mark uncertainty explicitly.** If you're not sure something is correct, say so: "⚠️ untested — verify before relying on". Worse than a gap is a confidently wrong statement.

**Quote sparingly.** For user decisions, a short direct quote ("user said: 'no auth on this endpoint'") is more reliable than paraphrase. But don't paste entire messages.

**Don't include secrets.** Reference env var names, never values. If credentials came up in conversation, note "credentials discussed — not recorded here" and move on.

**Date everything.** Top of file gets today's date. If you reference "yesterday's decision", convert to an actual date.

## Process

1. **Locate the target.** Default to `./HANDOFF.md` at the current working directory. If the user is clearly in a subproject, ask.
2. **Check for existing file.** If one exists, follow the rule in "When this skill is active" above.
3. **Gather facts.** Before writing, quickly scan: what files did you touch this session? What commands ran successfully? What did the user decide? What's still open?
4. **Draft the file.** Fill the template. Omit no sections without an explicit N/A.
5. **Verify paths exist.** Any file path you cite should actually exist. Run a quick `ls` or `view` if uncertain.
6. **Self-review pass.** Reread as if you're the next agent who knows nothing. Can you resume? What's missing?
7. **Show the user.** Either display the file or summarize what you wrote and where. Ask if anything important was missed.

## Anti-patterns to avoid

- ❌ Dumping the full conversation transcript
- ❌ Vague next steps ("continue the refactor") — be specific
- ❌ Recommending commands you didn't actually run
- ❌ Including the user's name, email, or other identifying info beyond what's already in the repo
- ❌ Writing in first-person narrative ("I tried X, then I noticed Y...") — use declarative facts
- ❌ Recapping things the next agent can see in `git log` or `git diff` — point to it instead
