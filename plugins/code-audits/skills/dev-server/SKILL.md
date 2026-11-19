---
name: dev-server
description: "Start the project's dev server (or a static server for a plain HTML prototype) AND open Chrome in debug mode through the Chrome DevTools MCP so Claude can control the running app. Use when the user wants to launch or run the dev server, see the app in the browser, or says \"/dev-server\", \"start the app\", \"run the dev server\", \"open the app in Chrome\", \"lance le serveur de dev\", \"démarre l'app\"."
---

Goal: start (1) the project's dev server and (2) Chrome in debug mode driven by the **Chrome
DevTools MCP**, in a **dedicated, isolated instance** (so that another Claude session does not
drive your page), in order to control the app: navigate, click, read the console, network and DOM,
take screenshots.

## 0. Prerequisite: Chrome DevTools MCP

This plugin bundles the Chrome DevTools MCP server (`chrome-devtools`, started with
`npx -y chrome-devtools-mcp@latest --isolated`). Check that it is available (tools
`navigate_page`, `take_snapshot`…) with `claude mcp list` or `/mcp` (expected: `chrome-devtools`
connected). Google Chrome and Node.js (for `npx`) are required too.

If it is not connected, find out why before going further. If nothing works: the skill stops after
starting the server (§1 to §3) and gives the URL to open by hand.

**Common case on macOS, Node managed by nvm** (or fnm, asdf…): the MCP is started without the
version manager's `PATH`, `npx` and `node` cannot be found and the server shows "Failed to
connect". **Offer** the workaround below and wait for consent (it installs a global npm package and
changes the Claude Code config): install globally and point to the **absolute paths** of node and
the script, in a user-scope server.

```bash
npm i -g chrome-devtools-mcp
NODE="$(command -v node)"                                   # e.g. ~/.nvm/versions/node/vX/bin/node
SCRIPT="$(npm prefix -g)/lib/node_modules/chrome-devtools-mcp/build/src/bin/chrome-devtools-mcp.js"
claude mcp add -s user chrome-devtools -- "$NODE" "$SCRIPT" --isolated
claude mcp list   # check that it is connected
```

The absolute path depends on the Node version: after a version change, run the `add` again. After
any MCP change, **restart Claude Code**: an MCP added during a session is not loaded. This setup is
**per machine**.

**Why `--isolated`.** Without this flag, `chrome-devtools-mcp` reuses a **fixed shared profile**
(`~/.cache/chrome-devtools-mcp/chrome-profile`): two concurrent Claude sessions can land on the
**same** Chrome and drive each other. With `--isolated`, each MCP process (so each session) creates
a unique temporary `user-data-dir`: a dedicated Chrome instance, no collision. The profile is
ephemeral: it lasts for the session and starts fresh at the next one. If you configured your own
server, check that it contains `--isolated` (`claude mcp get chrome-devtools`); otherwise run the
`add` again and restart Claude Code (an MCP config change is only read at startup).

### 0bis. (Optional) Remembered DevTools layout, per project

To get a precise DevTools layout back at every launch (DevTools in a separate window, **Network**
tab and console **drawer** open, **Device Toolbar** in Responsive 1920×1080 100 % Desktop), you need
a **persistent profile**: these settings are internal DevTools UI (dock, active panel, drawer,
device mode), stored in the `user-data-dir` (`Preferences`, key `devtools.preferences`). Neither a
flag nor the MCP controls them; only a profile that remembers them brings them back. `--isolated`
(throwaway profile) therefore resets them every time.

Trade-off: a **dedicated persistent profile per project**, through an MCP config at **local
scope** (private, attached to this project, taking precedence over the bundled and `user`
configs). Isolation stays the rule elsewhere, and a collision is only possible between two
sessions on the same project in parallel.

In the project concerned (with the absolute paths of §0 if Node goes through nvm):

```bash
NODE="$(command -v node)"
SCRIPT="$(npm prefix -g)/lib/node_modules/chrome-devtools-mcp/build/src/bin/chrome-devtools-mcp.js"
claude mcp add -s local chrome-devtools -- "$NODE" "$SCRIPT" \
  --userDataDir="$HOME/.cache/chrome-devtools-mcp/<project>-profile" \
  --viewport=1920x1080 \
  --chromeArg=--auto-open-devtools-for-tabs
```

No `-s project`: it would write paths specific to your machine into the project's versioned
`.mcp.json`. The `local` scope is stored in `~/.claude.json`, under this project's entry.

Then restart Claude Code, start the server (§1 onwards) and, **once only**, arrange DevTools by
hand: separate window, **Network** tab, console drawer (Esc), **Device Toolbar** in Responsive
1920×1080, 100 %, Desktop. Close Chrome: the preferences are written to the profile, and everything
reopens the same way at the next launches.

Notes:
- `--auto-open-devtools-for-tabs` **opens** DevTools at startup; the profile governs **how** it
  opens. If the automatic opening disturbs driving (two CDP clients), remove the flag and open
  DevTools by hand (⌥⌘I): the layout still comes back from the profile.
- Config **per machine**, to redo on each computer.
- The profile lives in `~/.cache`, outside the project: nothing to ignore in git.

## 1. Detect the server command

**JS project**: find the `package.json` of the current folder or the closest parent.
- **Monorepo** (`workspaces` in `package.json`, `pnpm-workspace.yaml`, `turbo.json`, `nx.json`,
  `lerna.json`): if there are several runnable applications, ask which one, then use the root
  script that targets it (`pnpm --filter <app> dev`, `npx turbo run dev --filter <app>`,
  `npx nx serve <app>`) or the one in the application's `package.json`.
- Script, in order of preference: `dev`, `start`, `serve`.
- Package manager from the lockfile: `pnpm-lock.yaml` → `pnpm`, `yarn.lock` → `yarn`,
  `bun.lock` or `bun.lockb` → `bun`, `package-lock.json` or nothing → `npm`. A `packageManager`
  field in `package.json` takes precedence.
- Command: `<pm> run <script>` (e.g. `pnpm run dev`).

**Static HTML prototype** (`.html` files without `package.json`, such as the prototypes built with
`living-specs:proto-bar` when that plugin is installed): offer a static server on a free port, at
the root of the prototype: `python3 -m http.server <port>` (URL
`http://localhost:<port>/<file>.html`), or `npx serve -l <port>` if Node is there. A plain
`file://` is enough to display it, but some behaviors (`fetch` of local files, ES modules) need a
server.

**Other project** (not JS, or no script): ask the user for the command.

## 2. Start the server in the background

Run the command with **`run_in_background: true`** (the server must stay up for the whole
session). Read the task output to get the local URL (e.g. `Local: http://localhost:5173/`). Do not
assume the port: read it from the output. Port already in use: the server often picks another one,
take the one it announces.

## 3. Wait for the server to answer

Wait until the URL answers, or a "ready" or "Local:" line appears in the output, with a limit: one
minute by default, more for a first build known to be slow. For example:

```bash
for i in $(seq 1 60); do curl -s -o /dev/null "<url>" && exit 0; sleep 1; done; exit 1
```

Do not open Chrome before that. **Failure** (timeout, or the task stopped): read the end of the
task output, show the error to the user (dependencies not installed, missing environment variable,
port taken, Node version), propose the obvious fix without applying it unasked (for example
installing the dependencies), and stop the task if it is still running.

## 4. Open the app in Chrome (Chrome DevTools MCP)

Navigate to **the URL detected in §2** with `navigate_page` (or `new_page`). The MCP starts Chrome
in debug mode, visible.

**Switch to that page**: select it as the active page (`list_pages` then `select_page`), so that
what follows targets the app that was started. A freshly started Chrome (especially with
`--isolated`) often opens on `about:blank` or another tab. Do not drive blind: confirm the URL
before acting.

## 5. Check and hand back

Take a `take_snapshot` (or a screenshot) to confirm that the app started is the one that loaded.
Announce: the URL, that the server runs in the background, and that control of the page is
available (navigation, clicks, console, network, DOM, screenshots).

## Notes

- The server stays in the background; to stop it, stop the corresponding task.
