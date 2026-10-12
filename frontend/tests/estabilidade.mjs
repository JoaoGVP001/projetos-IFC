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
const pasta = await mkdtemp(resolve(tmpdir(), "cadernomat-estabilidade-e2e-"));
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
    ["tests/webview_estabilidade_fixture.py"],
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
  await fill("Mensagem", "Explique indução matemática.");
  await click("Enviar mensagem");
  await wait(async () =>
    (await estado()).mensagens.some((m) => m.estado === "incompleta"),
  );
  const partial = (await estado()).mensagens.find(
    (m) => m.estado === "incompleta",
  );
  assert.equal(partial.metricas.motivo, "limite_saida");
  await wait(() => evaluate('!!document.querySelector(".response-warning")'));
  assert.equal(
    await evaluate(
      'document.querySelector(".response-warning").closest("code")',
    ),
    null,
  );
  await captura("estabilidade-aviso-claro.png");
  await writeFile(resolve(pasta, "concluir"), "1");
  await click("Próxima parte");
  await wait(() =>
    evaluate('document.body.innerText.includes("Dados e contexto enviados")'),
  );
  assert.equal((await estado()).mensagens.length, 2);
  await click("Enviar esta parte");
  await wait(
    async () =>
      (await estado()).mensagens.length === 4 && !(await estado()).ocupado,
  );
  assert.equal(
    (await estado()).mensagens[3].origem_consulta,
    partial.consulta_id,
  );
  await click("Configurações de IA");
  await click("Testar conexão e listar modelos");
  await wait(() =>
    evaluate('document.body.innerText.includes("Execução atual: CPU")'),
  );
  await fill("Perfil de resposta", "estudo");
  assert.equal(
    await evaluate(`document.querySelector('input[type="number"]').value`),
    "240",
  );
  await fecharDialogo();
  await click("Ilustração de indução");
  await click("Criar ilustração local");
  await wait(() =>
    evaluate('!!document.querySelector(".induction-figure img")'),
  );
  await evaluate(
    'document.querySelector(".induction-figure").scrollIntoView({block:"center"});true',
  );
  await captura("estabilidade-inducao-claro.png");
  const image = (await estado()).calculos.find(
    (j) => j.versao === "inducao-visual-v1",
  );
  const page = await rpc("pagina_criar", {
    caderno: null,
    mensagem: image.mensagem_id,
  });
  await rpc("pagina_salvar", { id: page.id });
  const job = await rpc("pagina_exportar", { id: page.id, versao: 1 });
  await wait(
    async () =>
      (await rpc("pagina_job", { id: job.id })).estado !== "executando",
  );
  assert.equal((await rpc("pagina_job", { id: job.id })).estado, "concluida");
  await click("Usar tema escuro");
  await cmd("Emulation.setDeviceMetricsOverride", {
    width: 1000,
    height: 650,
    deviceScaleFactor: 1,
    mobile: false,
  });
  await captura("estabilidade-minima-escuro.png");
  assert.ok(await evaluate("document.documentElement.scrollWidth<=1000"));
  await fechar();
  await iniciar();
  await wait(() =>
    evaluate('!!document.querySelector(".induction-figure img")'),
  );
  assert.equal(
    (await estado()).mensagens.filter((m) => m.estado === "incompleta").length,
    1,
  );
  const bridge = await evaluate(
    `(async()=>{const a=[];for(let i=0;i<5;i++){const t=performance.now();await window.pywebview.api.request("estado",{});a.push(performance.now()-t);}return a})()`,
  );
  console.log("Bridge estado (5 amostras, ms): " + JSON.stringify(bridge));
  assert.deepEqual(errosPagina, []);
  console.log(
    "E2E estabilidade OK: interrupção com métricas/aviso externo, prévia, continuação, diagnóstico CPU, perfis, ilustração, PDF, reinício e temas.",
  );
} catch (e) {
  if (ws?.readyState === 1)
    await captura("falha-estabilidade.png").catch(() => {});
  throw new Error(`${e.stack}\n${log}`);
} finally {
  await fechar().catch(() => {});
  if (ws?.readyState === 1) ws.close();
  await rm(pasta, { recursive: true, force: true });
}
