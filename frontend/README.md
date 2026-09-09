# InGen Studio — frontend

React 19 single-page app built on **Next.js 15 (App Router)**. The UI is fully client-rendered: the
data store lives in browser `localStorage` (mock mode) or talks to the FastAPI wrapper (http mode).

## Develop

```bash
npm install
npm run dev      # next dev — http://localhost:3000
```

The app redirects `/` to the seed config workspace, then on to its first interface editor.

## Scripts

| Script          | What it does                                  |
| --------------- | --------------------------------------------- |
| `npm run dev`   | Start the Next dev server (HMR)               |
| `npm run build` | Production build (`.next/`)                   |
| `npm run start` | Serve the production build                    |
| `npm run lint`  | ESLint (flat config)                          |
| `npm run test`  | Node test runner over `src/**/*.test.js`      |

## Configuration

Runtime config is read from `NEXT_PUBLIC_*` env vars (see `.env.example`):

- `NEXT_PUBLIC_ADAPTER_MODE` — `mock` (default; localStorage + simulated runs) or `http` (FastAPI wrapper)
- `NEXT_PUBLIC_API_BASE_URL` — FastAPI base URL, used only in `http` mode

Copy `.env.example` to `.env.local` to override locally. `.env.http` is a ready-made http-mode preset.

## Routing

Routes are file-based under `src/app/`:

```
src/app/
  layout.jsx                                  root shell (BootGate + AppShell brand bar)
  page.jsx                                    redirects to the seed config
  not-found.jsx
  configs/[configId]/
    layout.jsx                                catalog + config providers + WorkspaceLayout
    page.jsx                                  redirects to the first interface
    interfaces/[interfaceName]/page.jsx       InterfaceEditor
    sources/page.jsx                          SourcesRegistry
    run/page.jsx                              RunConsole
    history/page.jsx                          HistoryView
```

Imports use the `@/*` alias (→ `src/*`) where convenient; see `jsconfig.json`.
