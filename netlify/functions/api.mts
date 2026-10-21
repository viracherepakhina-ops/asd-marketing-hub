import { getStore } from "@netlify/blobs";
import type { Config, Context } from "@netlify/functions";
import seed from "../../tools/site-data.json" with { type: "json" };

const COLS = ["events", "materials", "orders"] as const;
type Col = (typeof COLS)[number];
const store = () => getStore({ name: "hub", consistency: "strong" });
const json = (body: unknown, status = 200) => Response.json(body, { status });
const isAdmin = (req: Request) => {
  const key = Netlify.env.get("ADMIN_KEY");
  return !!key && req.headers.get("x-admin-key") === key;
};
const newId = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 7);

async function seedIfEmpty(s: ReturnType<typeof store>) {
  if (await s.get("_seeded")) return;
  for (const e of (seed as any).events) { const { id, ...d } = e; await s.setJSON(`events/${id}`, d); }
  for (const m of (seed as any).materials) { const { id, ...d } = m; await s.setJSON(`materials/${id}`, d); }
  await s.set("_seeded", new Date().toISOString());
}

async function list(s: ReturnType<typeof store>, col: Col) {
  const { blobs } = await s.list({ prefix: `${col}/` });
  const docs = await Promise.all(blobs.map(async (b) => {
    const data = await s.get(b.key, { type: "json" });
    return data ? { id: b.key.slice(col.length + 1), ...(data as object) } : null;
  }));
  return docs.filter(Boolean);
}

export default async (req: Request, context: Context) => {
  const col = context.params.col as Col;
  const id = context.params.id;
  if (col === ("auth" as Col)) return json({ ok: isAdmin(req) }, isAdmin(req) ? 200 : 401);
  if (!COLS.includes(col)) return json({ error: "Unknown collection" }, 404);
  if (id && !/^[A-Za-z0-9._~:@+-]{1,200}$/.test(id)) return json({ error: "Bad id" }, 400);
  const s = store();
  await seedIfEmpty(s);
  const admin = isAdmin(req);

  if (req.method === "GET") return json({ docs: await list(s, col) });

  // Managers may only create orders; everything else is admin-only.
  if (!(admin || (req.method === "POST" && col === "orders" && !id))) return json({ error: "Admin key required" }, 401);

  if (req.method === "POST" && !id) {
    const body = await req.json().catch(() => null);
    if (!body || typeof body !== "object" || Array.isArray(body)) return json({ error: "Body must be an object" }, 400);
    const nid = newId();
    const doc = col === "orders" ? { ...body, status: "Not sent", sentDate: "", tracking: "", createdAt: new Date().toISOString() } : body;
    await s.setJSON(`${col}/${nid}`, doc);
    return json({ id: nid }, 201);
  }
  if (!id) return json({ error: "Missing id" }, 400);
  const key = `${col}/${id}`;
  if (req.method === "PUT") {
    const body = await req.json().catch(() => null);
    if (!body || typeof body !== "object" || Array.isArray(body)) return json({ error: "Body must be an object" }, 400);
    await s.setJSON(key, body);
    return json({ id });
  }
  if (req.method === "PATCH") {
    const cur = await s.get(key, { type: "json" });
    if (!cur) return json({ error: "Not found" }, 404);
    const body = await req.json().catch(() => null);
    if (!body || typeof body !== "object" || Array.isArray(body)) return json({ error: "Body must be an object" }, 400);
    await s.setJSON(key, { ...(cur as object), ...body });
    return json({ id });
  }
  if (req.method === "DELETE") { await s.delete(key); return json({ id }); }
  return json({ error: "Method not allowed" }, 405);
};

export const config: Config = { path: ["/api/:col", "/api/:col/:id"] };
