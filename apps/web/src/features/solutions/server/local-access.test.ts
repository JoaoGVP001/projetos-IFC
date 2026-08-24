import { describe, expect, it } from "vitest";

import { localAccessDenied } from "./local-access";

describe("private local access", () => {
  it("permite solicitações locais do próprio site", () => {
    expect(localAccessDenied(new Request("http://localhost:3000/api/solutions"))).toBeNull();
  });

  it("bloqueia host remoto e carregamento iniciado por outro site", async () => {
    const remote = localAccessDenied(new Request("https://resolvehub.example/api/solutions"));
    expect(remote?.status).toBe(403);

    const crossSite = localAccessDenied(new Request("http://localhost:3000/api/solutions", {
      headers: { "Sec-Fetch-Site": "cross-site" },
    }));
    expect(crossSite?.status).toBe(403);
    await expect(crossSite?.json()).resolves.toMatchObject({ error: expect.stringContaining("cruzado") });
  });
});
