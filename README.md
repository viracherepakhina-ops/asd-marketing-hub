# ASD Marketing Hub

Event calendar and marketing-materials request site for ASD Lighting account managers.
Live: https://asd-marketing-hub.netlify.app (access code required). Admin: add `#admin` to the URL.

- `site/index.html` — the page Netlify publishes (built from `tools/template.html` by `tools/build.py`).
- `netlify/functions/api.mts` — `/api/events`, `/api/materials`, `/api/orders`, stored in Netlify Blobs (store `hub`).
  First run seeds events and materials from `tools/site-data.json`. Writes other than new orders need the `ADMIN_KEY` env var (header `x-admin-key`).
- Each new request is also posted to Netlify Forms (`material-request`) so email notifications can be set up in the Netlify UI.

Published automatically by Netlify from the `main` branch.
