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
  await evaluate('document.querySelector(".page-ai").open=true;true');
  await evaluate(
    'document.querySelector(".page-ai input[type=checkbox]").click();true',
  );
  const beforeProposal = await rpc("pagina_obter", { id: pid });
  await writeFile(resolve(pasta, "formula-invalida"), "1");
  await click("Preparar proposta de página");
  await click("Pedir organização à IA");
  await wait(() => evaluate('document.body.innerText.includes("notação de fórmulas selecionadas")'));
  assert.deepEqual((await rpc("pagina_obter", { id: pid })).rascunho, beforeProposal.rascunho);
  assert.equal((await rpc("pagina_obter", { id: pid })).versao, 1);
  assert.equal(await evaluate('Array.from(document.querySelectorAll("button")).some(b=>b.textContent.includes("Aplicar proposta ao rascunho"))'), false);
  await evaluate('document.querySelector(".page-ai [role=alert]").scrollIntoView({block:"center"});true');
  assert.ok(await evaluate('(()=>{const r=document.querySelector(".page-ai [role=alert]").getBoundingClientRect();return r.top>=0&&r.bottom<=window.innerHeight})()'));
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
