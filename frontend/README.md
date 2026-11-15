# HVAC Air Freshener Front End

A React control panel for [pi_hvac_controller](https://github.com/kcmodev/pi_hvac_controller), a Raspberry Pi that sprays air freshener into a home's return duct while the HVAC system runs. From a phone or browser, it shows what the system is doing and triggers a spray on demand.

Built with React 19, TypeScript, Material UI and Vite, and tested with Vitest and React Testing Library.

## Features

- Shows the current HVAC state and the time of the last spray when opened
- Triggers a manual spray, disabling the button and showing progress during the cycle of about 15 seconds
- Shows the controller's message when a spray fails, such as when the sprayer is already running
- Can be added to a phone's home screen as a standalone app, through its web app manifest

## Getting started

Requires Node.js 26 (`nvm use` picks it up from `.nvmrc`) and a running [controller](https://github.com/kcmodev/pi_hvac_controller). The controller runs on a Mac or PC with simulated hardware, so a Pi isn't needed for development.

```bash
git clone https://github.com/kcmodev/hvac_front_end.git
cd hvac_front_end
npm install
npm run dev   # http://localhost:3000
```

### How it reaches the controller

The app calls the controller at `/api` on its own address, so neither needs to know where the other is hosted:

| Running as                 | What answers `/api`                                                        |
| -------------------------- | -------------------------------------------------------------------------- |
| `npm run dev` or `preview` | Vite forwards it to `API_PROXY_TARGET`, by default `http://127.0.0.1:8000` |
| Deployed on the Pi         | nginx forwards it to the controller's API                                  |

To develop against the real system, copy `.env.example` to `.env` and set `API_PROXY_TARGET` to the Pi's address. Sprays from the page are then real ones.

## Deploying

The app is served by nginx on the Pi, next to the controller. Set that up first by following [Deploying on the Pi](https://github.com/kcmodev/pi_hvac_controller#deploying-on-the-pi) in the controller's README. Then build here and copy the files over:

```bash
npm run build
rsync -a --delete dist/ pi@<pi-address>:/var/www/hvac/
```

The page updates on the next reload, with no restart needed. To try a build from another device on your network first, run `npm run preview -- --host`.

## Scripts

| Command           | Purpose                         |
| ----------------- | ------------------------------- |
| `npm run dev`     | Start the development server    |
| `npm run build`   | Type-check and build to `dist/` |
| `npm run preview` | Serve the production build      |
| `npm test`        | Run the tests                   |
| `npm run lint`    | Run ESLint                      |
| `npm run format`  | Format with Prettier            |

## Project layout

```
├── index.html
├── public/             Icon and web app manifest
└── src/
    ├── api.ts          Typed client for the controller's API
    ├── App.tsx         Control panel
    └── main.tsx        Entry point and theme
```

The tests sit beside the code they cover, and need no controller or hardware.

## Security

Like the controller's API, this app has no authentication. Anyone who can reach it can trigger a spray, so keep both on a trusted home network.

## License

[MIT](LICENSE)
