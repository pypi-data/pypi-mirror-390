# Daily Notes - Claude Code Instructions

## Context
You're in the `daily/` folder where daily journal entries are stored.

## Daily Note Format
Each file is named `YYYY-MM-DD.md` and follows the daily-template structure:
- Morning section (energy, intentions, priorities)
- Throughout the day (timestamped updates)
- Evening reflection

## Your Role Here

### When User Starts Their Day
```
User: "Let's start the day"
You:
1. Check if today's note exists (YYYY-MM-DD.md)
2. If not, create it from daily-template.md
3. Ask about sleep quality, energy level
4. Help set intentions and priorities
5. Ask about desired emotional outcomes
```

### Throughout the Day
Proactively update today's note as conversations happen:
```
User: "Just wrapped up that client call"
You: [Add timestamped entry to today's note]
     "**2:30 PM** - Completed client call. [add any key points they mention]"
```

### Evening Check-In
```
User: "Update my daily note"
You: Guide reflection:
- What went well?
- What was challenging?
- What did you learn?
- Energy level now vs morning?
- Tomorrow's top priority?
```

## Template Reference
Load with: `resolve_template("daily-template.md", journal_path)`

## Remember
- Keep entries conversational and natural
- Capture the human experience, not just tasks
- Notice energy patterns over time
- Celebrate wins, no matter how small
