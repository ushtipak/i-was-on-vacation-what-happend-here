# I Was On Vacation — What Happened Here?!

> Claude Code is the orchestrator. Follow the steps below to turn a Slack channel's backlog into a beautiful meme recap page.

---

## What this does

1. Reads message history from a Slack channel via the Slack MCP
2. Groups messages into 5–10 major events / themes
3. Picks the perfect imgflip meme template for each event
4. Captions it with something funny and contextually accurate
5. Renders `output/index.html` — a shareable meme recap page

---

## Prerequisites (check before running)

- `IMGFLIP_USERNAME` and `IMGFLIP_PASSWORD` are set in the environment
  (free account at https://imgflip.com/signup is enough)
- Slack MCP is configured and the bot has access to the target channel
- Python 3.8+ is available (`python3 --version`)

---

## How to run

### Step 1 — Ask the user

Before doing anything, ask:
- **Which Slack channel?** (e.g. `#general`, `#engineering`, `#random`)
- **How far back?** (e.g. "last 2 weeks", "since April 1st", "while I was on vacation April 3–14")

### Step 2 — Fetch Slack messages

Use the Slack MCP to:
1. `slack_list_channels` — find the channel ID for the requested channel name
2. `slack_get_channel_history` — fetch messages for the requested period
   - Fetch in batches (the tool may have a limit per call); keep paginating until you have everything
   - Also call `slack_get_thread_replies` for any message that has a `reply_count > 0` — threads often contain the most important context

Collect the raw messages. Note usernames / display names so the recap feels personal.

### Step 3 — Analyse and group into events

Read ALL the messages carefully. Then identify **5 to 10 major events** — things that actually mattered:
- A big incident, outage, or fire drill
- A shipped feature or launch
- A long debate that went nowhere
- A running joke that took over the channel
- Someone's brilliant (or terrible) idea
- A decision that was made (or avoided)
- Drama, celebrations, surprises

For each event write:
- **Event name** — punchy, 3–6 words (e.g. "The Redis Meltdown of Tuesday")
- **One-line summary** — what actually happened
- **Meme angle** — why it's funny / relatable / absurd

> Skip: routine stand-up messages, bot notifications, link-only messages, "ok", "lgtm", "+1" noise.

### Step 4 — Get meme templates

```bash
python3 meme_maker.py templates
```

This prints the top 40 imgflip templates with their IDs. Study the list. Match each event to the most fitting template. Think about:
- **Drake Pointing** — rejecting old thing, approving new thing
- **Distracted Boyfriend** — team abandoning X for Y
- **Two Buttons** — impossible choice / paralysis
- **This is Fine** — chaos being ignored
- **Change My Mind** — controversial take someone actually took
- **Expanding Brain** — escalating sequence of increasingly unhinged decisions
- **Surprised Pikachu** — obvious outcome nobody saw coming
- **Gru's Plan** — plan that backfired
- **Left Exit 12** — sudden pivot away from something
- **Woman Yelling at Cat** — someone being unreasonable vs. calm response

### Step 5 — Create the memes

For each event, run:

```bash
python3 meme_maker.py create \
  --id     <TEMPLATE_ID> \
  --top    "<top caption>" \
  --bottom "<bottom caption>" \
  --event  "<Event Name>" \
  --summary "<one-line summary>" \
  --template-name "<Template Name>"
```

Caption writing rules:
- **Be specific** — name the actual thing that happened, not a generic joke
- **Top text sets up**, bottom text delivers the punchline
- Keep each caption under ~60 characters so it fits on the image
- Match the energy: dry for incidents, chaotic for debates, warm for wins
- If the event had a protagonist, name them (first name is fine)

### Step 6 — Generate the HTML recap

```bash
python3 meme_maker.py html
```

Then open the file:

```bash
xdg-open output/index.html 2>/dev/null || open output/index.html 2>/dev/null || echo "Open: $(pwd)/output/index.html"
```

### Step 7 — Tell the user

Report back:
- How many messages were processed
- The events you identified (brief list)
- Where the HTML file is
- Any meme you're particularly proud of

---

## Utility commands

```bash
python3 meme_maker.py clear   # wipe output/ and start over
python3 meme_maker.py templates --limit 100   # see more templates
```

---

## Tone guide

This is a **fun** tool. The captions should make the person reading them snort-laugh in recognition, not cringe at a generic AI joke. If a caption feels like it could apply to any company anywhere, rewrite it. Specificity = funny.
