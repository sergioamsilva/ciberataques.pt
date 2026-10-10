import type { APIRoute } from "astro";
import { MARCA_SVG } from "../lib/marca";

export const GET: APIRoute = () =>
  new Response(MARCA_SVG, { headers: { "Content-Type": "image/svg+xml" } });
