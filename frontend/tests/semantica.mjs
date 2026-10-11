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
const pasta = await mkdtemp(resolve(tmpdir(), "cadernomat-local-e2e-"));
const capturas = resolve(raiz, "docs/screenshots");
await mkdir(capturas, { recursive: true });
await writeFile(
  resolve(pasta, "notas.txt"),
  "Regulamento fictício do mini-simulado: 7 questões e 23 minutos.\n",
);
const real = process.env.CADERNOMAT_REAL_LOCAL === "1";
const ollamaPort = real ? 11434 : await portaLivre();
const modelo = real ? "qwen3.5:4b-q4_K_M" : "teste:4b";
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
    ["tests/webview_semantica_fixture.py"],
    {
      cwd: raiz,
      env: {
        ...process.env,
        CADERNOMAT_TEST_DIR: pasta,
        CADERNOMAT_OLLAMA_PORT: String(ollamaPort),
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
  for (let i = 0; i < (real ? 1800 : 200); i++) {
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
  if (ws?.readyState === 1) ws.close();
  if (proc?.exitCode === null) {
    const saida = new Promise((r) => proc.once("exit", r));
    await writeFile(resolve(pasta, "sair"), "1");
    const acabou = await Promise.race([
      saida.then(() => true),
      sleep(7000).then(() => false),
    ]);
    if (!acabou) {
      proc.kill("SIGTERM");
      throw new Error("Fechamento normal da janela excedeu o limite");
    }
  }
  await unlink(resolve(pasta, "sair")).catch(() => {});
}
async function rpc(op, dados = {}) {
  return evaluate(
    `window.pywebview.api.request(${JSON.stringify(op)},${JSON.stringify(dados)}).then(r=>{if(!r.ok)throw Error(r.error);return r.data})`,
  );
}
try {
  await iniciar();
  const cid = (await estado()).conversa.id;
  await evaluate(
    `Array.from(document.querySelectorAll('button')).find(b=>b.textContent.includes('Materiais') && b.textContent.includes('Biblioteca')).click()`,
  );
  await wait(() => evaluate('!!document.querySelector(".semantic-panel")'));
  await evaluate(`document.querySelector('.semantic-panel').open=true`);
  await click("Indexar / retomar e ativar");
  await wait(
    async () =>
      (await rpc("semantica_status")).trabalho?.estado === "concluido",
  );
  assert.equal((await estado()).anexos[0].selecionado, false);
  await evaluate(
    `const s=document.querySelector('[aria-label="Modo de busca nos materiais"]');s.value='hibrida';s.dispatchEvent(new Event('change',{bubbles:true}));`,
  );
  await evaluate(`document.querySelector('.semantic-panel').open=false`);
  await fill("Buscar materiais", "inclinação de uma curva num ponto");
  await wait(() => evaluate(`!!document.querySelector('.semantic-hit')`));
  assert.ok((await texto()).includes("apostila.txt"));
  assert.ok((await texto()).includes("busca semântica local"));
  await evaluate(
    `Array.from(document.querySelectorAll('button')).find(b=>b.textContent==='Do caderno atual').click()`,
  );
  await wait(() =>
    evaluate(`document.querySelectorAll('.material-card').length===1`),
  );
  await click("Consultar apostila.txt neste chat");
  await wait(async () => (await estado()).anexos[0].selecionado);
  const preview = await rpc("previa", {
    id: cid,
    texto: "inclinação de uma curva num ponto",
    modo: "Explicar",
  });
  assert.equal(preview.fontes.length, 1);
  assert.equal(preview.fontes[0].nome, "apostila.txt");
  assert.equal(preview.recuperacao.metodo, "busca híbrida local");
  await captura(
    process.env.CADERNOMAT_REAL_SEMANTICA === "1"
      ? "busca-semantica-real.png"
      : "busca-semantica-simulada.png",
  );
  console.log(
    "Qt: indexação explícita, busca por significado, filtros e seleção autorizada OK",
  );
  const before = await rpc("semantica_status");
  await fechar();
  await iniciar();
  const after = await rpc("semantica_status");
  assert.equal(after.indexados, before.indexados);
  assert.equal(after.habilitada, 1);
  assert.equal((await estado()).conversa.id, cid);
  assert.equal((await estado()).anexos[0].selecionado, true);
  if (process.env.CADERNOMAT_REAL_SEMANTICA === "1") {
    const isolated = JSON.parse(
      await readFile(resolve(pasta, "isolamento.json"), "utf8"),
    );
    console.log("Isolamento Qt:", isolated);
    assert.ok(
      isolated.namespace_separado && isolated.conexao_externa_bloqueada,
    );
  }
  await evaluate(
    `Array.from(document.querySelectorAll('button')).find(b=>b.getAttribute('aria-label')==='Abrir materiais').click()`,
  );
  await wait(() => evaluate('!!document.querySelector(".semantic-panel")'));
  await cmd("Emulation.setDeviceMetricsOverride", {
    width: 1000,
    height: 650,
    deviceScaleFactor: 1,
    mobile: false,
  });
  await rpc("preferencias", { tema: "escuro" });
  await wait(() =>
    evaluate("document.documentElement.dataset.theme==='escuro'"),
  );
  assert.ok(await evaluate("document.documentElement.scrollWidth<=innerWidth"));
  assert.deepEqual(errosPagina, []);
  console.log("Qt: índice, chat e seleção preservados ao reiniciar OK");
} catch (e) {
  if (ws?.readyState === 1)
    await captura("falha-semantica-e2e.png").catch(() => {});
  throw new Error(`${e.stack}\n${log}`);
} finally {
  await fechar().catch(() => {});
  if (ws?.readyState === 1) ws.close();
  await rm(pasta, { recursive: true, force: true });
}
