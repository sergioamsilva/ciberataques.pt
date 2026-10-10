import type { APIRoute } from "astro";
import { pngDaMarca } from "../lib/marca";

export const GET: APIRoute = () =>
  new Response(pngDaMarca(180) as BodyInit, { headers: { "Content-Type": "image/png" } });
