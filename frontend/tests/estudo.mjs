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
const pasta = await mkdtemp(resolve(tmpdir(), "cadernomat-estudo-e2e-"));
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
    ["tests/webview_estudo_fixture.py"],
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
  await fill("Mensagem", "Explique a derivada da funcao quadratica.");
  await fill("Modo de estudo", "Consultar materiais");
  await click("Enviar mensagem");
  await wait(() =>
    evaluate('document.body.innerText.includes("Enviar com estas fontes")'),
  );
  const previewText = await texto();
  assert.ok(previewText.includes("página 2"));
  assert.ok(previewText.includes("Derivada"));
  assert.equal((await estado()).mensagens.length, 0);
  await click("Enviar com estas fontes");
  await wait(async () =>
    (await estado()).mensagens.some(
      (m) => m.papel === "assistant" && m.estado === "ok",
    ),
  );
  const first = (await estado()).mensagens.find((m) => m.papel === "assistant");
  const snapshots = await rpc("consulta_fontes", { mensagem: first.id });
  assert.equal(snapshots.fontes[0].pagina, 2);
  assert.ok(snapshots.fontes[0].texto.includes("2x-4"));
  await wait(() => evaluate('!!document.querySelector(".consulted-sources")'));
  await evaluate('document.querySelector(".consulted-sources").open=true;true');
  await wait(() =>
    evaluate('document.body.innerText.includes("Trecho exato enviado")'),
  );
  await click("Ver página do original");
  await wait(() =>
    evaluate('!!document.querySelector(".source-original")?.naturalWidth'),
  );
  await evaluate(
    'document.querySelector(".consulted-sources").scrollIntoView({block:"start"});true',
  );
  await captura("estudo-fontes-claro.png");
  await click("Conferir operação de Cálculo");
  await click("Exemplo da parábola");
  await click("Calcular e salvar no chat");
  await wait(async () =>
    (await estado()).calculos.some(
      (j) => j.tipo === "calculo" && j.estado === "concluida",
    ),
  );
  const calc = (await estado()).calculos.find(
    (j) => j.tipo === "calculo" && j.estado === "concluida",
  );
  const local = await rpc("math_obter", { id: calc.id });
  assert.equal(local.previa.origem_estudo.mensagem, first.id);
  assert.deepEqual(
    local.previa.origem_estudo.fontes[0].texto,
    snapshots.fontes[0].texto,
  );
  const page = await rpc("pagina_criar", {
    caderno: (await estado()).navegacao.caderno_id,
    mensagem: first.id,
  });
  await rpc("pagina_calculo", { id: page.id, calculo: calc.id });
  const current = await rpc("pagina_obter", { id: page.id });
  const plan = await rpc("pagina_organizar", {
    id: page.id,
    secoes: current.rascunho.secoes.map((s) => s.id),
  });
  await rpc("pagina_aceitar", { id: page.id, trabalho: plan.id });
  const saved = await rpc("pagina_salvar", { id: page.id });
  const exportJob = await rpc("pagina_exportar", {
    id: page.id,
    versao: saved.versao,
  });
  await wait(
    async () =>
      (await rpc("pagina_job", { id: exportJob.id })).estado !== "executando",
  );
  assert.equal(
    (await rpc("pagina_job", { id: exportJob.id })).estado,
    "concluida",
  );
  // Guarda as folhas geradas antes de remover a fixture.
  const { readdir, copyFile } = await import("node:fs/promises");
  const exported = resolve(pasta, "paginas/exportacoes", exportJob.id);
  for (const file of await readdir(exported))
    if (file.endsWith(".png") || file.endsWith(".pdf"))
      await copyFile(
        resolve(exported, file),
        resolve(capturas, "estudo-" + file),
      );
  await fechar();
  await iniciar();
  assert.deepEqual(
    (await rpc("consulta_fontes", { mensagem: first.id })).fontes,
    snapshots.fontes,
  );
  assert.equal(
    (await rpc("math_obter", { id: calc.id })).previa.origem_estudo.mensagem,
    first.id,
  );
  assert.deepEqual(
    (await rpc("pagina_obter", { id: page.id })).render.referencias[0].snapshot
      .texto,
    snapshots.fontes[0].texto,
  );
  await wait(() => evaluate('!!document.querySelector(".consulted-sources")'));
  await evaluate('document.querySelector(".consulted-sources").open=true;true');
  await wait(() =>
    evaluate('document.body.innerText.includes("Trecho exato enviado")'),
  );
  const mid = (await estado()).anexos[0].id;
  await rpc("material_acao", { id: mid, acao: "excluir", confirmado: true });
  await evaluate(
    'document.querySelector(".consulted-sources").open=false;document.querySelector(".consulted-sources").open=true;true',
  );
  await wait(() =>
    evaluate(
      'document.body.innerText.includes("Material removido; o trecho utilizado foi preservado")',
    ),
  );
  assert.equal(
    await evaluate(
      'Array.from(document.querySelectorAll(".consulted-sources button")).find(b=>b.textContent.includes("Abrir arquivo original"))?.disabled',
    ),
    true,
  );
  await click("Usar tema escuro");
  await cmd("Emulation.setDeviceMetricsOverride", {
    width: 1000,
    height: 650,
    deviceScaleFactor: 1,
    mobile: false,
  });
  await evaluate(
    'document.querySelector(".consulted-sources").scrollIntoView({block:"start"});true',
  );
  await captura("estudo-fontes-removidas-escuro.png");
  assert.ok(await evaluate("document.documentElement.scrollWidth<=1000"));
  assert.deepEqual(errosPagina, []);
  console.log(
    "E2E estudo confiável OK: prévia sem envio, trecho/página, operação local vinculada, página fiel/PDF/PNG, reinício, remoção sem perda do snapshot e temas.",
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
