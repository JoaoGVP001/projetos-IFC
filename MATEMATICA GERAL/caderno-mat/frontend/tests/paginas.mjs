// Fluxo real no Qt WebEngine: CDP nativo (Qt nao implementa contextos do Playwright).
import { spawn } from "node:child_process";
import {
  mkdtemp,
  writeFile,
  readFile,
  unlink,
  mkdir,
  rm,
} from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";
import { createServer } from "node:net";

const raiz = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const pasta = await mkdtemp(resolve(tmpdir(), "cadernomat-paginas-e2e-"));
const capturas =
  process.env.CADERNOMAT_SCREENSHOTS_DIR || resolve(raiz, "docs/screenshots");
await mkdir(capturas, { recursive: true });
await writeFile(
  resolve(pasta, "notas.txt"),
  "Regulamento fictício do mini-simulado: 7 questões e 23 minutos.\n",
);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let proc,
  ws,
  numero = 0,
  log = "",
  errosPagina = [];
const espera = new Map();
async function portaLivre() {
  const s = createServer();
  await new Promise((r) => s.listen(0, "127.0.0.1", r));
  const p = s.address().port;
  await new Promise((r) => s.close(r));
  return p;
}
async function iniciar() {
  log = "";
  const porta = await portaLivre();
  proc = spawn(
    process.env.CADERNOMAT_PYTHON || resolve(raiz, ".venv/bin/python"),
    ["tests/webview_paginas_fixture.py"],
    {
      cwd: raiz,
      env: {
        ...process.env,
        CADERNOMAT_TEST_DIR: pasta,
        QTWEBENGINE_REMOTE_DEBUGGING: `127.0.0.1:${porta}`,
      },
      stdio: ["ignore", "pipe", "pipe"],
    },
  );
  proc.stdout.on("data", (b) => (log += b));
  proc.stderr.on("data", (b) => (log += b));
  let alvo;
  for (let i = 0; i < 150; i++) {
    if (proc.exitCode !== null) throw new Error(`Janela encerrou: ${log}`);
    try {
      const alvos = await (
        await fetch(`http://127.0.0.1:${porta}/json/list`)
      ).json();
      alvo = alvos.find((t) => t.type === "page");
      if (alvo) break;
    } catch {}
    await sleep(100);
  }
  if (!alvo) throw new Error(`WebView nao iniciou: ${log}`);
  ws = new WebSocket(alvo.webSocketDebuggerUrl);
  await new Promise((r, j) => {
    ws.onopen = r;
    ws.onerror = j;
  });
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    if (m.id) {
      const p = espera.get(m.id);
      if (p) {
        espera.delete(m.id);
        clearTimeout(p.timer);
        m.error
          ? p.reject(new Error(JSON.stringify(m.error)))
          : p.resolve(m.result);
      }
    } else if (m.method === "Runtime.exceptionThrown")
      errosPagina.push(m.params.exceptionDetails.text);
  };
  await cmd("Runtime.enable");
  await wait(() =>
    evaluate(`!!document.querySelector('[aria-label="Novo chat"]')`),
  );
}
function cmd(method, params = {}) {
  return new Promise((r, j) => {
    const id = ++numero;
    const timer = setTimeout(() => {
      espera.delete(id);
      j(new Error(`Timeout CDP: ${method}`));
    }, 15000);
    espera.set(id, { resolve: r, reject: j, timer });
    ws.send(JSON.stringify({ id, method, params }));
  });
}
async function evaluate(expression) {
  const r = await cmd("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
  if (r.exceptionDetails)
    throw new Error(
      r.exceptionDetails.exception?.description || r.exceptionDetails.text,
    );
  return r.result?.value;
}
async function wait(fn) {
  for (let i = 0; i < 200; i++) {
    if (await fn()) return;
    await sleep(100);
  }
  throw new Error("Condicao nao alcançada");
}
const localizar = `function alvo(nome){return document.querySelector('[aria-label="'+CSS.escape(nome)+'"]')||document.querySelector('[title="'+CSS.escape(nome)+'"]')||Array.from(document.querySelectorAll('label.field')).find(l=>l.firstElementChild?.textContent===nome)?.querySelector('input,textarea,select')||Array.from(document.querySelectorAll('button,[role="menuitem"]')).find(b=>b.textContent.trim()===nome&&b.checkVisibility())}`;
async function click(nome) {
  await wait(() =>
    evaluate(
      `(()=>{${localizar};const e=alvo(${JSON.stringify(nome)});return !!e&&!e.disabled})()`,
    ),
  );
  await evaluate(
    `(()=>{${localizar};const e=alvo(${JSON.stringify(nome)});if(!e||e.disabled)throw Error('Botao ausente/desabilitado: '+${JSON.stringify(nome)});e.click();return true})()`,
  );
}
async function fill(nome, valor) {
  await wait(() =>
    evaluate(
      `(()=>{${localizar};const e=alvo(${JSON.stringify(nome)});return !!e&&!e.disabled})()`,
    ),
  );
  await evaluate(
    `(()=>{${localizar};const e=alvo(${JSON.stringify(nome)});if(!e||e.disabled)throw Error('Campo indisponivel');e.focus();const prot=e.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:e.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;Object.getOwnPropertyDescriptor(prot,'value').set.call(e,${JSON.stringify(valor)});e.dispatchEvent(new Event(e.tagName==='SELECT'?'change':'input',{bubbles:true}));return true})()`,
  );
}
async function estado() {
  return evaluate(
    'window.pywebview.api.request("estado",{}).then(r=>{if(!r.ok)throw Error(r.error);return r.data})',
  );
}
async function texto() {
  return evaluate("document.body.innerText");
}
async function fecharDialogo() {
  await click("Fechar diálogo");
  await wait(() => evaluate('!document.querySelector("dialog")'));
}
async function captura(nome) {
  await sleep(300);
  const { data } = await cmd("Page.captureScreenshot", { format: "png" });
  await writeFile(resolve(capturas, nome), Buffer.from(data, "base64"));
}
async function fechar() {
  if (proc?.exitCode === null) {
    const saida = new Promise((r) => proc.once("exit", r));
    await writeFile(resolve(pasta, "sair"), "1");
    const acabou = await Promise.race([
      saida.then(() => true),
      sleep(10000).then(() => false),
    ]);
    if (!acabou) {
      if (ws?.readyState === 1)
        log += JSON.stringify(
          await evaluate(
            '({ready:window.cadernoMatPageCloseReady,error:window.cadernoMatPageCloseError,draft:window.cadernoMatPageDraft,alerts:Array.from(document.querySelectorAll("[role=alert],[role=status]")).map(e=>e.textContent)})',
          ),
        );
      proc.kill("SIGTERM");
      throw new Error("Fechamento normal da janela excedeu o limite");
    }
  }
  if (ws?.readyState === 1) ws.close();
  await unlink(resolve(pasta, "sair")).catch(() => {});
}
async function rpc(op, dados = {}) {
  return evaluate(
    `window.pywebview.api.request(${JSON.stringify(op)},${JSON.stringify(dados)}).then(r=>{if(!r.ok)throw Error(r.error);return r.data})`,
  );
}
try {
  await iniciar();
  const state = await estado();
  await click("Abrir páginas de estudo");
  await click("Nova página");
  await fill("Título da página", "Cálculo e Discreta — estudo");
  await fill(
    "Conteúdo da seção 1",
    "Considere $f(x)=x^2-4x+3$.\n\n$$f'(x)=2x-4$$\n\nMínimo: $(2,-1)$.",
  );
  await click("Salvar versão");
  const pid = (await estado()).pagina;
  await wait(async () => (await rpc("pagina_obter", { id: pid })).versao === 1);
  assert.equal((await rpc("pagina_obter", { id: pid })).versao, 1);
  await click("Visualizar folhas");
  await wait(() => evaluate('!!document.querySelector(".study-sheet .katex")'));
  await captura("paginas-previa-claro.png");
  await click("Editar página");
  await evaluate(
    'Array.from(document.querySelectorAll("summary")).find(x=>x.textContent==="Versões, exportação e biblioteca").parentElement.open=true;true',
  );
  await click("Gerar PDF e PNG");
  await wait(async () => {
    const js = await rpc("pagina_jobs", { id: pid });
    return js.some((j) => j.tipo === "exportacao" && j.estado === "concluida");
  });
  await click("Salvar PDF no computador");
  await wait(async () =>
    Boolean(await readFile(resolve(pasta, "copia.pdf")).catch(() => null)),
  );
  assert.ok(
    (await readFile(resolve(pasta, "copia.pdf")))
      .subarray(0, 4)
      .equals(Buffer.from("%PDF")),
  );
  await click("Salvar folhas PNG");
  await click("Adicionar versão revisada à biblioteca");
  await wait(async () => {
    const m = await rpc("materiais", {
      busca: "Cálculo e Discreta",
      caderno: state.conversa.caderno_id,
    });
    return m.itens.length === 1;
  });
  const material = (
    await rpc("materiais", {
      busca: "Cálculo e Discreta",
      caderno: state.conversa.caderno_id,
    })
  ).itens[0];
  assert.equal(material.selecionado, false);
  await evaluate(
    'document.querySelector(".page-ai:not(.page-faithful)").open=true;true',
  );
  await evaluate(
    'document.querySelector(".page-ai:not(.page-faithful) input[type=checkbox]").click();true',
  );
  const beforeProposal = await rpc("pagina_obter", { id: pid });
  await writeFile(resolve(pasta, "formula-invalida"), "1");
  await click("Preparar proposta de página");
  await click("Pedir organização à IA");
  await wait(() =>
    evaluate(
      'document.body.innerText.includes("notação de fórmulas selecionadas")',
    ),
  );
  assert.deepEqual(
    (await rpc("pagina_obter", { id: pid })).rascunho,
    beforeProposal.rascunho,
  );
  assert.equal((await rpc("pagina_obter", { id: pid })).versao, 1);
  assert.equal(
    await evaluate(
      'Array.from(document.querySelectorAll("button")).some(b=>b.textContent.includes("Aplicar proposta ao rascunho"))',
    ),
    false,
  );
  await evaluate(
    'document.querySelector(".page-ai:not(.page-faithful) [role=alert]").scrollIntoView({block:"center"});true',
  );
  assert.ok(
    await evaluate(
      '(()=>{const r=document.querySelector(".page-ai:not(.page-faithful) [role=alert]").getBoundingClientRect();return r.top>=0&&r.bottom<=window.innerHeight})()',
    ),
  );
  await captura("paginas-formula-preservada.png");
  await unlink(resolve(pasta, "formula-invalida"));
  await click("Preparar proposta de página");
  await click("Pedir organização à IA");
  await wait(() =>
    evaluate('document.body.innerText.includes("Proposta editável")'),
  );
  assert.equal(
    (await rpc("pagina_obter", { id: pid })).rascunho.titulo,
    "Cálculo e Discreta — estudo",
  );
  await click("Aplicar proposta ao rascunho");
  await wait(() =>
    evaluate(
      `document.querySelector('[aria-label="Título da página"]')?.value==="Revisão organizada"`,
    ),
  );
  await fill("Conteúdo da seção 1", "Último caractere preservado: !");
  await fechar();
  await iniciar();
  const restored = await rpc("pagina_obter", { id: pid });
  assert.equal(
    restored.rascunho.secoes[0].texto,
    "Último caractere preservado: !",
  );
  assert.equal(restored.versao, 1);
  assert.equal(
    (await rpc("pagina_versao", { id: pid, versao: 1 })).conteudo.titulo,
    "Cálculo e Discreta — estudo",
  );
  await writeFile(resolve(pasta, "falhar-autosave"), "1");
  await fill(
    "Conteúdo da seção 1",
    "Rascunho preservado após falha ao fechar.",
  );
  await writeFile(resolve(pasta, "sair"), "1");
  await wait(() => evaluate("window.cadernoMatPageCloseReady === false"));
  assert.equal(
    await evaluate("window.cadernoMatPageDraft.conteudo.secoes[0].texto"),
    "Rascunho preservado após falha ao fechar.",
  );
  await unlink(resolve(pasta, "falhar-autosave"));
  await click("Salvar versão");
  await wait(async () => (await rpc("pagina_obter", { id: pid })).versao === 2);
  await click("Usar tema escuro");
  await cmd("Emulation.setDeviceMetricsOverride", {
    width: 1000,
    height: 650,
    deviceScaleFactor: 1,
    mobile: false,
  });
  await captura("paginas-minima-escuro.png");
  assert.ok(await evaluate("document.documentElement.scrollWidth<=1000"));
  await evaluate(
    'document.querySelector(".chats .chat-row button").click();true',
  );
  await click("Criar página de estudo");
  await wait(() =>
    evaluate(`!!document.querySelector('[aria-label="Título da página"]')`),
  );
  await evaluate(
    'document.querySelector(".chats .chat-row button").click();true',
  );
  await wait(() =>
    evaluate(
      'Array.from(document.querySelectorAll("button")).some(b=>b.textContent.includes("Ver página:"))',
    ),
  );
  await evaluate(
    'Array.from(document.querySelectorAll("button")).find(b=>b.textContent.includes("Ver página:")).click();true',
  );
  await wait(() =>
    evaluate('!!document.querySelector("dialog .study-sheet .katex")'),
  );
  await click("Abrir editor da página");
  await wait(() =>
    evaluate(
      `!document.querySelector("dialog") && !!document.querySelector('[aria-label="Título da página"]')`,
    ),
  );
  // Mensagem -> organização fiel local -> IA por IDs -> exportação e reinício.
  const faithfulPid = (await estado()).pagina;
  await fill(
    "Conteúdo da seção 1",
    "Para todo inteiro $n\\ge 1$: $1+2+\\cdots+n=\\frac{n(n+1)}{2}$.\n\nFixe k arbitrário, use P(k), prove P(k+1) e conclua para todo n >= 1.\n\n$$\\begin{aligned}S_{k+1}&=S_k+(k+1)\\\\&=\\frac{(k+1)(k+2)}{2}\\end{aligned}$$",
  );
  await click("Salvar versão");
  const induction = await rpc("inducao_executar", {
    conversa: (await estado()).conversa.id,
    spec: { inicio: 1, proposicao: "Soma dos naturais" },
  });
  await wait(
    async () =>
      (await rpc("inducao_obter", { id: induction.id })).estado === "concluida",
  );
  await rpc("pagina_calculo", { id: faithfulPid, calculo: induction.id });
  await fechar();
  await iniciar();
  await wait(() => evaluate('!!document.querySelector(".page-faithful")'));
  await wait(
    async () =>
      (await rpc("pagina_obter", { id: faithfulPid })).rascunho.secoes
        .length === 2,
  );
  const faithfulOriginal = await rpc("pagina_obter", { id: faithfulPid });
  await evaluate('document.querySelector(".page-faithful").open=true;true');
  await click("Preservar seção 1");
  await click("Preservar seção 2");
  await click("Preparar organização local");
  await wait(() =>
    evaluate(
      '!!document.querySelector(".page-faithful .study-sheet img") && !!document.querySelector(".page-faithful .katex")',
    ),
  );
  assert.deepEqual(
    (await rpc("pagina_obter", { id: faithfulPid })).rascunho,
    faithfulOriginal.rascunho,
  );
  const faithfulJob = (await rpc("pagina_jobs", { id: faithfulPid })).find(
    (j) => j.tipo === "organizacao" && j.estado === "concluida",
  );
  await evaluate(
    'Array.from(document.querySelectorAll(".page-faithful summary")).find(s=>s.textContent.includes("Texto preservado integral")).parentElement.open=true;true',
  );
  assert.deepEqual(
    await evaluate(
      'JSON.parse(Array.from(document.querySelectorAll(".page-faithful summary")).find(s=>s.textContent.includes("Texto preservado integral")).parentElement.querySelector("pre").textContent)',
    ),
    faithfulJob.resultado,
  );
  await cmd("Emulation.setDeviceMetricsOverride", {
    width: 1000,
    height: 650,
    deviceScaleFactor: 1,
    mobile: false,
  });
  await evaluate(
    'document.querySelector(".page-faithful").scrollIntoView({block:"start"});true',
  );
  await captura("fidelidade-previa-escuro.png");
  await click("Aplicar organização preservando o original");
  await wait(
    async () =>
      (await rpc("pagina_obter", { id: faithfulPid })).versao ===
      faithfulOriginal.versao + 1,
  );
  const faithfulApplied = await rpc("pagina_obter", { id: faithfulPid });
  assert.deepEqual(
    (
      await rpc("pagina_versao", {
        id: faithfulPid,
        versao: faithfulApplied.versao,
      })
    ).conteudo,
    faithfulOriginal.rascunho,
  );
  assert.deepEqual(
    faithfulApplied.render.recursos,
    faithfulOriginal.render.recursos,
  );
  await evaluate('document.querySelector(".page-faithful").open=true;true');
  await click("Preservar seção 1");
  await writeFile(resolve(pasta, "ids-invalidos"), "1");
  await click("Preparar rótulos com IA");
  await click("Pedir rótulos à IA");
  await wait(() =>
    evaluate(
      'document.querySelector(".page-faithful [role=alert]")?.textContent.includes("ordem obrigatória")',
    ),
  );
  assert.deepEqual(
    (await rpc("pagina_obter", { id: faithfulPid })).rascunho,
    faithfulApplied.rascunho,
  );
  await evaluate(
    'document.querySelector(".page-faithful [role=alert]").scrollIntoView({block:"center"});true',
  );
  assert.ok(
    await evaluate(
      '(()=>{const r=document.querySelector(".page-faithful [role=alert]").getBoundingClientRect();return r.top>=0&&r.bottom<=window.innerHeight})()',
    ),
  );
  await unlink(resolve(pasta, "ids-invalidos"));
  await click("Preparar rótulos com IA");
  await click("Pedir rótulos à IA");
  await wait(() =>
    evaluate(
      'document.querySelector(".page-faithful .study-sheet")?.textContent.includes("sugerido pela IA")',
    ),
  );
  await click("Aplicar organização preservando o original");
  await wait(
    async () =>
      (await rpc("pagina_obter", { id: faithfulPid })).rascunho.secoes[0]
        .rotulo_origem === "ia",
  );
  await click("Salvar versão");
  const faithfulFinal = await rpc("pagina_obter", { id: faithfulPid });
  await evaluate(
    'Array.from(document.querySelectorAll("summary")).find(x=>x.textContent==="Versões, exportação e biblioteca").parentElement.open=true;true',
  );
  await click("Gerar PDF e PNG");
  await wait(async () =>
    (await rpc("pagina_jobs", { id: faithfulPid })).some(
      (j) => j.tipo === "exportacao" && j.estado === "concluida",
    ),
  );
  await click("Salvar PDF no computador");
  // Guarda as folhas afetadas para inspeção visual, antes de limpar a fixture.
  await click("Salvar folhas PNG");
  const { readdir, copyFile } = await import("node:fs/promises");
  const exportJob = (await rpc("pagina_jobs", { id: faithfulPid })).find(
    (j) =>
      j.tipo === "exportacao" &&
      j.versao === faithfulFinal.versao &&
      j.estado === "concluida",
  );
  const pngDir = resolve(pasta, "pngs", "pagina-" + exportJob.id.slice(0, 8));
  await wait(async () => Boolean(await readdir(pngDir).catch(() => null)));
  for (const name of await readdir(pngDir))
    if (name.endsWith(".png"))
      await copyFile(
        resolve(pngDir, name),
        resolve(capturas, "fidelidade-" + name),
      );
  await copyFile(
    resolve(pasta, "copia.pdf"),
    resolve(capturas, "fidelidade-aceite.pdf"),
  );
  await fechar();
  await iniciar();
  assert.deepEqual(
    (await rpc("pagina_obter", { id: faithfulPid })).rascunho,
    faithfulFinal.rascunho,
  );
  await cmd("Emulation.setDeviceMetricsOverride", {
    width: 1000,
    height: 650,
    deviceScaleFactor: 1,
    mobile: false,
  });
  await click("Visualizar folhas");
  await wait(() => evaluate('!!document.querySelector(".study-sheet img")'));
  await click("Usar tema claro");
  await captura("fidelidade-reinicio-claro.png");
  assert.ok(await evaluate("document.documentElement.scrollWidth<=1000"));
  assert.deepEqual(errosPagina, []);
  console.log(
    "E2E páginas OK: editor, versão, prévia KaTeX, PDF/PNG reais, biblioteca sem seleção, proposta revisável, fechamento imediato, reinício, tema, janela mínima e prévia no chat.",
  );
} catch (e) {
  if (ws?.readyState === 1)
    await captura("falha-paginas-e2e.png").catch(() => {});
  throw new Error(`${e.stack}\n${log}`);
} finally {
  await fechar().catch(() => {});
  if (ws?.readyState === 1) ws.close();
  await rm(pasta, { recursive: true, force: true });
}
