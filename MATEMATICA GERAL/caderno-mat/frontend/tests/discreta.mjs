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
const pasta = await mkdtemp(resolve(tmpdir(), "cadernomat-discreta-e2e-"));
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
    ["tests/webview_discreta_fixture.py"],
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
  async function tool(kind) {
    await click("Matemática Discreta");
    await fill("Ferramenta de Discreta", kind);
    await click("Carregar exemplo de Discreta");
    await click("Conferir dados interpretados");
  }
  async function compute() {
    const before = (await estado()).calculos.length;
    await click("Calcular e salvar Discreta");
    await wait(async () => {
      const s = await estado();
      return (
        !s.ocupado &&
        s.calculos.length > before &&
        s.calculos.at(-1).estado === "concluida"
      );
    });
    await wait(() =>
      evaluate(
        'Array.from(document.querySelectorAll("dialog [role=status]")).some(x=>x.textContent.includes("Resultado salvo no chat"))',
      ),
    );
    return rpc("discreta_obter", { id: (await estado()).calculos.at(-1).id });
  }
  await tool("conjuntos");
  await captura("discreta-conjuntos-claro.png");
  const sets = await compute();
  assert.equal(sets.resultado.resultados.cardinalidade_A, 3);
  assert.deepEqual(sets.resultado.resultados.uniao, [1, 2, 3, 4]);
  await fecharDialogo();
  await wait(() =>
    evaluate('!!document.querySelector(".math-artifact img")?.complete'),
  );
  await click("Exportar diagrama PNG");
  await wait(async () =>
    Boolean(
      await readFile(resolve(pasta, "diagrama-exportado.png")).catch(
        () => null,
      ),
    ),
  );
  assert.ok(
    (await readFile(resolve(pasta, "diagrama-exportado.png")))
      .subarray(0, 8)
      .equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])),
  );
  await tool("relacoes");
  const rel = await compute();
  assert.deepEqual(
    rel.resultado.resultados.propriedades.find(
      (p) => p.propriedade === "transitiva",
    ).contraexemplo,
    [1, 2, 3],
  );
  await evaluate(
    'document.querySelector("dialog .math-artifact").scrollIntoView({block:"center"});true',
  );
  await captura("discreta-relacoes-claro.png");
  await fecharDialogo();
  await tool("logica");
  const logic = await compute();
  assert.equal(logic.resultado.resultados.equivalentes, true);
  await fecharDialogo();
  await wait(() => evaluate('!!document.querySelector(".table-scroll table")'));
  await evaluate('document.querySelector(".table-scroll table").scrollIntoView({block:"start"});true');
  await captura("discreta-logica-claro.png");
  await click("Matemática Discreta");
  await evaluate('document.querySelector("dialog .math-ai").open=true');
  await fill("Pedido para IA", "Verifique R={(1,2),(2,3)} sobre A={1,2,3}.");
  await click("Preparar proposta da IA");
  await click("Pedir proposta à IA");
  await wait(async () => !(await estado()).ocupado);
  const prop = (await estado()).calculos.at(-1);
  const proposal = await rpc("discreta_obter", { id: prop.id });
  assert.equal(proposal.resultado.A, "{1,2,3}");
  assert.equal(proposal.resultado.U, "");
  assert.equal(proposal.tipo, "proposta");
  await wait(() =>
    evaluate(
      `document.querySelector('dialog input[aria-label="Conjunto A"]').value==="{1,2,3}"`,
    ),
  );
  await click("Conferir dados interpretados");
  const linked = await compute();
  assert.equal(linked.proposta_id, prop.id);
  await fecharDialogo();
  await click("Usar tema escuro");
  await click("Matemática Discreta");
  await cmd("Emulation.setDeviceMetricsOverride", {
    width: 1000,
    height: 650,
    deviceScaleFactor: 1,
    mobile: false,
  });
  await captura("discreta-minima-escuro.png");
  assert.ok(await evaluate("document.documentElement.scrollWidth<=1000"));
  await fecharDialogo();
  await cmd("Emulation.clearDeviceMetricsOverride");
  await fechar();
  await iniciar();
  assert.equal(
    (await rpc("discreta_obter", { id: sets.id })).imagem,
    sets.imagem,
  );
  assert.equal(
    (await rpc("discreta_obter", { id: logic.id })).resultado.resultados
      .equivalentes,
    true,
  );
  const aid = (
    await rpc("atividade_salvar", {
      caderno: (await estado()).conversa.caderno_id,
      conteudo: {
        titulo: "Relações — prática",
        exercicios: [
          {
            id: "q1",
            formato: "vf",
            enunciado: "Para A={1,2,3} e R={(1,2),(2,3)}, R é transitiva?",
            resposta: false,
            explicacao: "Falta (1,3).",
          },
        ],
      },
    })
  ).id;
  const attempt = await rpc("tentativa_iniciar", { atividade: aid });
  await rpc("estudo_navegar", {
    area: "atividades",
    atividade: aid,
    tentativa: attempt.id,
  });
  await click("Abrir atividades");
  await wait(async () =>
    Boolean(
      await evaluate(
        'Array.from(document.querySelectorAll("button")).some(x=>x.textContent.trim()==="Ferramentas de Discreta")',
      ),
    ),
  );
  await click("Ferramentas de Discreta");
  await fill("Ferramenta de Discreta", "relacoes");
  await click("Carregar exemplo de Discreta");
  await click("Conferir dados interpretados");
  await click("Calcular e salvar Discreta");
  await wait(async () => {
    const rows = await rpc("discreta_vinculos", {
      atividade: aid,
      atividade_versao: 1,
      questao: "q1",
      tentativa: attempt.id,
    });
    return rows[0]?.estado === "concluida";
  });
  await wait(() => evaluate('Array.from(document.querySelectorAll("dialog [role=status]")).some(x=>x.textContent.includes("Resultado salvo no chat"))'));
  await fecharDialogo();
  await wait(() => evaluate('!!document.querySelector(".math-artifact details")'));
  await evaluate('document.querySelector(".math-artifact details").open=true;document.querySelector(".math-artifact").scrollIntoView({block:"start"});true');
  await captura("discreta-atividade-escuro.png");
  assert.equal(
    (await rpc("tentativa_obter", { id: attempt.id })).estado,
    "andamento",
  );
  assert.deepEqual(errosPagina, []);
  console.log(
    "E2E Discreta OK: conjuntos, relações, lógica, PNG, proposta revisável, proveniência, versão/tentativa, temas, janela mínima e reinício.",
  );
} catch (e) {
  if (ws?.readyState === 1)
    await captura("falha-discreta-e2e.png").catch(() => {});
  throw new Error(`${e.stack}\n${log}`);
} finally {
  await fechar().catch(() => {});
  if (ws?.readyState === 1) ws.close();
  await rm(pasta, { recursive: true, force: true });
}
