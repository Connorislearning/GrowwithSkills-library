# AGENTS.md

Guidance for any AI coding agent (Claude Code, Codex, Cursor, Copilot) working in this repository. `CLAUDE.md` points here.

## What this repository is for

Skill Library is the proof-of-work piece of Connor Hancer's portfolio. The portfolio's goal is to earn more money for Connor as a performance marketing / GTM engineer, from a full-time job or from clients. Every change here should help a hiring manager, founder, or client believe within a few minutes that Connor builds marketing systems that produce results, and should leave them one clear way to contact him.

The repository does two things from one Cloudflare Worker:

1. Serves a read-only MCP endpoint at `/mcp` so anyone can connect their own AI to the skills.
2. Serves a landing page at `/` that lists the skills and shows each skill's README.

The public name is "Skill Library". Do not use "Skill Dojo" anywhere (another product already uses that name). The license is MIT.

## This repository is public

Everything committed here, including every past commit, is visible to anyone. The Worker has no login, so everything it serves is public too.

- Never commit real ad-account exports (CSV, XLSX), client decks, client names, ad account IDs, or screenshots of real accounts. Example data must be made up, and labeled as made up. `.gitignore` blocks `*.csv` everywhere except `skills/*/*/samples/`, which holds only made-up sample data.
- Never commit a `paid-social-data/` folder or any `.db` file. That is a user's private local database.
- Meta API tokens are read only from environment variables or a git-ignored `.env`. Never write one into code, a sample, or a README.
- Never commit `.env`, `.dev.vars`, tokens, API keys, or a Cloudflare `account_id`. This Worker needs no secrets today. If one is ever needed, store it with `npx wrangler secret put NAME` (or as an encrypted secret in the Cloudflare dashboard), and never in `vars` in `wrangler.jsonc`, because `vars` are stored as plain text in this public file.
- A skill is published the moment its `SKILL.md` has `public: true` under `metadata:` and the change reaches `main`. Leave `public: true` off any draft. Note that a draft's files are still visible on GitHub even when the Worker does not serve them.
- Before a commit, run `git status` and `git diff --staged` and read what is being added. Do not use `git add -A` or `git add .` without reading the list.
- If a secret is ever committed, treat it as leaked even if the commit is removed later. Tell Connor, and rotate the secret first.

## How to write for Connor

- Plain language. Short sentences. No analogies or metaphors of any kind.
- Cite the source of any fact (a link, a file, or "Connor said on <date>"). Say when something is a guess.
- Build first and keep questions to a minimum. Use a clearly marked placeholder when a detail is missing.
- Skill READMEs are written in Connor's first-person voice and describe his step-by-step process. They are marketing as well as documentation.

## Commands

```
npm install          # install packages
npm run dev          # run the Worker locally (wrangler dev); bundles skills first
npm run deploy       # bundle skills and deploy to Cloudflare (wrangler deploy)
npm run type-check   # tsc --noEmit
npm run format       # oxfmt --write .
npm run lint:fix     # oxlint --fix
npm run cf-typegen   # regenerate worker-configuration.d.ts after changing wrangler.jsonc
node scripts/bundle-skills.mjs   # regenerate src/skills.generated.ts by hand
```

Tests (Python 3.9+, no installs):

```
python3 tests/check_skills.py   # skill format contract, store.py copies, no .env or .db files
python3 tests/run_samples.py    # runs every skill's "Try it" commands on its sample data
```

`src/skills.generated.ts` is ignored by git. On a fresh clone, `npm run type-check` fails until the bundler has run once (`node scripts/bundle-skills.mjs`, or `npm run dev`).

## Architecture

Two parts live here: the skills, and the Worker that serves them.

### Skills

- Layout follows the Agent Skills specification (agentskills.io/specification): `skills/<category>/<skill-name>/`. Categories today: `project-management` and `creative`.
- `SKILL.md` is for the AI. Frontmatter: `name` (must equal the folder name), `description` (one line, under 160 characters), `license: MIT`, and `metadata:` with `category`, `public`, `version`. Keep every value on one line. Write "the agent", never a specific AI product.
- `README.md` is for people, in Connor's first-person voice. It has a "Try it" section whose commands `tests/run_samples.py` runs.
- `scripts/` holds Python 3.9+ scripts, standard library only. Rule (Connor, 2026-11-27): anywhere code can do the job, use a script to save tokens; the AI only does judgment and writing. Scripts print JSON or tables the agent writes from.
- `samples/` holds made-up data for trying the scripts.
- `references/local-data-store.md` describes the shared local database.
- `shared/store.py` is the local SQLite database module. Each skill keeps an identical copy in `scripts/store.py` so it works when installed alone. Edit `shared/store.py`, then copy it to every skill; `tests/check_skills.py` fails if a copy differs.
- `docs/` holds the week overview (`media-buyers-week.md`) and the database spec (`local-data-store.md`).

### Worker

The flow is: Markdown files in `skills/` are packed into one TypeScript file at build time, and the Worker serves that file's contents. There is no database, no storage binding, and no runtime file access. The Worker serves only SKILL.md and README.md text, never scripts or samples.

- `scripts/bundle-skills.mjs` walks `skills/*/*/SKILL.md`, keeps the ones with `public: true`, and writes `src/skills.generated.ts`. Wrangler runs it before every `dev` and `deploy` through the `build.command` setting in `wrangler.jsonc`. Never edit the generated file by hand. The frontmatter parser is a simple line-by-line `key: value` reader (indented keys under `metadata:` are read too), so keep each value on one line.
- `src/index.ts` is the whole Worker. `GET /` returns the landing page, built as an HTML string by `homePage()`. Every other request goes to the MCP handler, which exposes two tools: `list_skills` and `get_skill`. Both only read from the bundled `SKILLS` array.
- The landing page's `md()` function is a very small Markdown converter. It only handles `## ` headings and paragraphs, and it escapes HTML. Lists, links, tables, and code blocks in a skill README will show as plain text on the landing page unless `md()` is extended.
- `worker-configuration.d.ts` is generated by Wrangler. Do not edit it by hand.

## Adding a skill

1. Create `skills/<category>/<name>/` with `SKILL.md`, `README.md`, and, where code can do the work, `scripts/` and `samples/`. Copy `shared/store.py` into `scripts/` if the skill saves data.
2. Add a row to the tables in the root `README.md` and `docs/media-buyers-week.md`.
3. Run both tests, then `npm run dev` and check the landing page and `list_skills`.
4. Set `public: true` only when the skill is ready to be seen.

Every skill ends with a rule that the AI must not put client names or account IDs in anything saved or shared, and with the marked "Want this run for you?" block. Keep both in new skills.

## Deploying

The intended setup is Cloudflare Workers Builds connected to this GitHub repository, so that each push to `main` redeploys the Worker. There is no local deploy script; Workers Builds is the only deploy path.

The Worker name is `growwithskills-library`, matching the GitHub repository name. The first deploy uses the `workers.dev` address. The custom domain `mcp.connorhancer.ai` is planned but is not configured in `wrangler.jsonc` yet, so check that any URL written in the README or the landing page actually works before publishing it.

The landing page should use the portfolio's "Tech Innovation" theme: Electric Blue `#0066ff`, Neon Cyan `#00ffff`, Dark Gray `#1e1e1e`, White `#ffffff`, with Space Grotesk for headings and Inter for body text.
