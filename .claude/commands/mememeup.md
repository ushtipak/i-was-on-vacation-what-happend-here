# /mememeup — Vacation Recap Meme Generator

Turn a Slack channel's backlog into a meme recap page for someone who was just on vacation.

## Arguments

The command accepts optional arguments: `$ARGUMENTS`

Parse `$ARGUMENTS` for:
- A number (e.g. `7`, `14`) → number of vacation days
- A Slack channel ID (e.g. `C09HH1557L0`) or name (e.g. `#general`)

---

## Step 1 — Gather inputs

If the number of vacation days was **not** provided in `$ARGUMENTS`, ask the user:
> "How many days were you on vacation?"

If the channel was **not** provided in `$ARGUMENTS`:
- Check the `SLACK_DEFAULT_CHANNEL` environment variable — if set, use that value.
- If not set, ask the user: *"Which Slack channel should I fetch? (e.g. `#general` or a channel ID like `C012AB3CD`)"*

Compute the start timestamp: today minus the number of vacation days.

---

## Step 2 — Fetch Slack messages

Use the Slack MCP:

1. Call `mcp__slack__conversations_history` with the channel ID and a limit of `<N>d` (e.g. `14d` for 14 days). Paginate using the cursor until you have all messages from the vacation period.
2. For every message that has a `reply_count > 0` (a thread), call `mcp__slack__conversations_replies` to fetch the full thread. Threads often contain the most important context.

Collect all messages. Note real names so the recap feels personal.

Ignore: bot messages, join/leave notifications, link-only messages, pure reactions, one-word replies ("ok", "lgtm", "+1").

---

## Step 3 — Identify 5–10 major events

Read ALL messages carefully. Group them into **5 to 10 major events** — things that actually mattered:

- A big incident, outage, or fire drill
- A shipped feature or launch
- A long debate or discussion
- A running joke that took over the channel
- A decision made (or avoided)
- Drama, celebrations, surprises, someone's wild idea

For each event write:
- **Event name** — punchy, 3–6 words (e.g. "The Redis Meltdown of Tuesday")
- **One-line summary** — what actually happened, with real names
- **Meme angle** — why it's funny / relatable / absurd

---

## Step 4 — Get meme templates

Run:
```bash
python3 meme_maker.py templates
```

Study the output. Match each event to the most fitting template. Think about:
- **Drake Pointing** — rejecting old thing, approving new thing
- **Distracted Boyfriend** — team abandoning X for Y
- **Two Buttons** — impossible choice / paralysis
- **This is Fine** — chaos being ignored
- **Change My Mind** — controversial take someone actually took
- **Expanding Brain** — escalating sequence of increasingly unhinged decisions
- **Surprised Pikachu** — obvious outcome nobody saw coming
- **Gru's Plan** — plan that backfired
- **Left Exit 12** — sudden pivot
- **Woman Yelling at Cat** — someone unreasonable vs. calm response

---

## Step 5 — Create the memes

For each event, run:

```bash
python3 meme_maker.py create \
  --id     "<TEMPLATE_ID>" \
  --top    "<top caption>" \
  --bottom "<bottom caption>" \
  --event  "<Event Name>" \
  --summary "<one-line summary>" \
  --template-name "<Template Name>"
```

Caption rules:
- **Be specific** — name the actual thing/person, not a generic joke
- Top text sets up, bottom text delivers the punchline
- Keep each caption under ~60 characters
- If a caption could apply to any company anywhere, rewrite it — specificity = funny

---

## Step 6 — Generate the HTML recap

```bash
python3 meme_maker.py html
```

Then open it:
```bash
xdg-open output/index.html 2>/dev/null || open output/index.html 2>/dev/null || echo "Open: $(pwd)/output/index.html"
```

---

## Step 7 — Report back

Tell the user:
- How many messages were processed and over what period
- The events you identified (brief list)
- Where the HTML file is
- Any meme you're particularly proud of
