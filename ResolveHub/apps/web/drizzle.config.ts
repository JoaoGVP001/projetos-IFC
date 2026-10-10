import { defineConfig } from "drizzle-kit";

export default defineConfig({
  dialect: "postgresql",
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  dbCredentials: {
    url: process.env.DATABASE_URL ?? "postgresql://resolvehub:resolvehub_dev_only@localhost:5432/resolvehub",
  },
  strict: true,
  verbose: true,
});
