import type { APIRoute } from "astro";
import { icoDaMarca } from "../lib/marca";

export const GET: APIRoute = () =>
  new Response(icoDaMarca(32) as BodyInit, { headers: { "Content-Type": "image/x-icon" } });
