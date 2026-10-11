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
    ["tests/webview_math_fixture.py"],
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
  await click("Cálculos e gráficos");
  await click("Exemplo da parábola");
  await captura("matematica-formulario-claro.png");
  await click("Calcular e salvar no chat");
  await wait(async () =>
    (await estado()).calculos.some(
      (j) => j.tipo === "calculo" && j.estado === "concluida",
    ),
  );
  const job = (await estado()).calculos.find((j) => j.tipo === "calculo");
  const result = await rpc("math_obter", { id: job.id });
  assert.equal(result.resultado.resultados[0].valor.texto, "2*x - 4");
  await wait(async () => (await texto()).includes("Mínimo absoluto em R"));
  await wait(() =>
    evaluate('!!document.querySelector(".math-artifact img")?.complete'),
  );
  await evaluate(
    'document.querySelector(".math-artifact").scrollIntoView({block:"center"})',
  );
  await captura("matematica-grafico-claro.png");
  await click("Exportar PNG");
  await wait(async () =>
    Boolean(
      await readFile(resolve(pasta, "grafico-exportado.png")).catch(() => null),
    ),
  );
  assert.ok(
    (await readFile(resolve(pasta, "grafico-exportado.png")))
      .subarray(0, 8)
      .equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])),
  );
  await fechar();
  await iniciar();
  assert.equal((await estado()).conversa.id, cid);
  assert.equal((await rpc("math_obter", { id: job.id })).imagem, result.imagem);
  await wait(() =>
    evaluate('!!document.querySelector(".math-artifact img")?.complete'),
  );
  await rpc("preferencias", { tema: "escuro" });
  await wait(() =>
    evaluate("document.documentElement.dataset.theme==='escuro'"),
  );
  await evaluate(
    'document.querySelector(".math-artifact").scrollIntoView({block:"center"})',
  );
  await captura("matematica-grafico-escuro.png");
  await cmd("Emulation.setDeviceMetricsOverride", {
    width: 1000,
    height: 650,
    deviceScaleFactor: 1,
    mobile: false,
  });
  assert.ok(await evaluate("document.documentElement.scrollWidth<=innerWidth"));
  await click("Cálculos e gráficos");
  await captura("matematica-minima-escuro.png");
  assert.ok(
    await evaluate('document.querySelector("dialog").scrollWidth<=innerWidth'),
  );
  await fecharDialogo();
  await cmd("Emulation.clearDeviceMetricsOverride");
  await click("Cálculos e gráficos");
  await evaluate("document.querySelector('.math-tools .math-ai').open=true");
  await fill(
    "Pedido para IA",
    "Trace f(x)=x^2-4*x+3 no intervalo [-2,6], calcule a derivada e a tangente em x=3.",
  );
  await click("Preparar proposta da IA");
  assert.equal(
    (await estado()).calculos.filter(
      (j) => j.tipo === "proposta" && j.estado === "executando",
    ).length,
    0,
  );
  await click("Pedir proposta à IA");
  await wait(() =>
    evaluate(
      "document.querySelector('[aria-label=\"Função f(x)\"]').value==='x^2-4*x+3'",
    ),
  );
  assert.equal(
    (await estado()).calculos.filter((j) => j.tipo === "calculo").length,
    1,
  );
  await captura("matematica-proposta-ia.png");
  await click("Calcular e salvar no chat");
  await wait(
    async () =>
      (await estado()).calculos.filter(
        (j) => j.tipo === "calculo" && j.estado === "concluida",
      ).length === 2,
  );
  await wait(() =>
    evaluate('document.querySelectorAll(".math-artifact").length===2'),
  );
  await evaluate("document.querySelector('.math-artifact .math-ai').open=true");
  await click("Preparar explicação da IA");
  await click("Pedir explicação à IA");
  await wait(async () => (await texto()).includes("Pergunta de prática:"));
  assert.equal(
    (await rpc("math_obter", { id: job.id })).resultado.resultados[0].valor
      .texto,
    "2*x - 4",
  );
  await evaluate(
    'Array.from(document.querySelectorAll(".message")).at(-1).scrollIntoView({block:"center"})',
  );
  await captura("matematica-explicacao-ia.png");
  await fechar();
  await iniciar();
  await wait(() =>
    evaluate(
      'Array.from(document.querySelectorAll("button")).some(b=>b.textContent==="Revisar proposta da IA")',
    ),
  );
  await click("Revisar proposta da IA");
  await wait(() =>
    evaluate("document.querySelector('[aria-label=\"Ponto x\"]')?.value==='3'"),
  );
  assert.deepEqual(errosPagina, []);
  console.log(
    "Qt L3: cálculo/PNG/exportação/reinício, proposta revisável e explicação de IA, temas/min-size OK",
  );
} catch (e) {
  if (ws?.readyState === 1)
    await captura("falha-matematica-e2e.png").catch(() => {});
  throw new Error(`${e.stack}\n${log}`);
} finally {
  await fechar().catch(() => {});
  if (ws?.readyState === 1) ws.close();
  await rm(pasta, { recursive: true, force: true });
}
