# ASD Marketing Hub

Event calendar and marketing-materials request site for ASD Lighting account managers.
Live: https://asd-marketing-hub.netlify.app (access code required).

- `site/` is what Netlify publishes. `site/data.js` holds events and materials.
- Material requests go to Netlify Forms (form name `material-request`).
- To change data: edit `tools/site-data.json`, then run `cd tools && python3 build.py`.
- To change design or behavior: edit `tools/template.html`, then run the same build.
