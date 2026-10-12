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
    ["tests/webview_local_fixture.py"],
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
  await click("Novo chat");
  await wait(async () => !!(await estado()).conversa);
  const cid = (await estado()).conversa.id;
  await click("Configurações de IA");
  await click("IA local · Ollama");
  assert.equal(
    await evaluate("!!document.querySelector('input[type=\"password\"]')"),
    false,
  );
  await fill("Modelo", modelo);
  await fill("Endereço do Ollama", `http://127.0.0.1:${ollamaPort}`);
  await click("Testar conexão e listar modelos");
  await wait(async () =>
    (await texto()).includes("Modelo de texto disponível"),
  );
  await captura(real ? "local-config-real.png" : "local-config-simulado.png");
  await click("Salvar configuração");
  await wait(() => evaluate('!document.querySelector("dialog")'));
  assert.equal((await estado()).config.escopo, "chat");
  assert.equal((await estado()).config.provedor, "ollama");
  console.log("Configuração local e metadados OK");
  await click("Anexar arquivos");
  await wait(async () => (await estado()).anexos[0]?.estado === "pronto");
  await click("Consultar notas.txt");
  await fill(
    "Mensagem",
    "Segundo o regulamento do mini-simulado, quantas questões há e qual o tempo? Cite [M1] e responda em até 80 palavras.",
  );
  await click("Prévia do envio");
  await wait(async () => (await texto()).includes("Orçamento do modelo local"));
  assert.ok((await texto()).includes("Somente Ollama neste computador"));
  await fecharDialogo();
  await click("Enviar mensagem");
  await wait(() =>
    evaluate('document.body.innerText.includes("Enviar com estas fontes")'),
  );
  await click("Enviar com estas fontes");
  await wait(
    async () =>
      !(await estado()).ocupado && (await estado()).mensagens.length === 2,
  );
  let s = await estado();
  assert.equal(s.mensagens[1].estado, "ok");
  assert.ok(
    s.mensagens[1].texto.includes("7") && s.mensagens[1].texto.includes("23"),
  );
  assert.equal(s.mensagens[1].provedor, "ollama");
  await wait(() => evaluate('!!document.querySelector(".message-assistant")'));
  await captura(real ? "local-chat-real.png" : "local-chat-simulado.png");
  console.log("Chat/RAG textual/citações OK");
  await fill(
    "Mensagem",
    "Explique a ideia de derivada com exemplos, em aproximadamente 200 palavras. Depois proponha dois exercícios de prática.",
  );
  await click("Enviar mensagem");
  await wait(() =>
    evaluate('document.body.innerText.includes("Enviar com estas fontes")'),
  );
  await click("Enviar com estas fontes");
  await wait(() =>
    evaluate(
      "!!document.querySelector('[aria-label=\"Resposta em geração\"] .markdown')",
    ),
  );
  await click("Cancelar resposta");
  await wait(async () => !(await estado()).ocupado);
  s = await estado();
  const erro = s.mensagens.at(-1);
  assert.equal(erro.estado, "cancelada");
  assert.ok(s.conversa.rascunho.includes("derivada"));
  await click("Repetir consulta");
  await wait(
    async () =>
      !(await estado()).ocupado && (await estado()).mensagens.length === 5,
  );
  s = await estado();
  assert.equal(s.mensagens.at(-1).estado, "ok");
  assert.equal(s.mensagens.filter((m) => m.papel === "user").length, 2);
  const mensagens = s.mensagens;
  await fechar();
  await iniciar();
  s = await estado();
  assert.equal(s.conversa.id, cid);
  assert.deepEqual(s.mensagens, mensagens);
  assert.equal(s.config.provedor, "ollama");
  assert.equal(s.anexos[0].selecionado, true);
  console.log("Streaming/cancelamento/repetição/reinício OK");
  if (real) {
    const isolated = JSON.parse(
      await readFile(resolve(pasta, "isolamento.json"), "utf8"),
    );
    assert.ok(
      isolated.namespace_separado && isolated.conexao_externa_bloqueada,
    );
    console.log(
      "Aceite real no Qt, modelo instalado e rede externa bloqueada OK",
    );
  }
  assert.deepEqual(errosPagina, []);
} catch (e) {
  if (ws?.readyState === 1)
    await captura("falha-local-e2e.png").catch(() => {});
  throw new Error(`${e.stack}\n${log}`);
} finally {
  await fechar().catch(() => {});
  if (ws?.readyState === 1) ws.close();
  await rm(pasta, { recursive: true, force: true });
}
