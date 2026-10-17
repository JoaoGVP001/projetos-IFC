// Fluxo real no Qt WebEngine: CDP nativo (Qt nao implementa contextos do Playwright).
import { spawn } from "node:child_process";
import { mkdtemp, writeFile, unlink, mkdir, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";
import { createServer } from "node:net";

const raiz = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const pasta = await mkdtemp(resolve(tmpdir(), "cadernomat-e2e-"));
const capturas =
  process.env.CADERNOMAT_SCREENSHOTS_DIR || resolve(raiz, "docs/screenshots");
await mkdir(capturas, { recursive: true });
await writeFile(
  resolve(pasta, "notas.txt"),
  "Derivada: taxa de variação instantânea de uma função. Para x²-4x+3, f'(x)=2x-4.\n",
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
    ["tests/webview_fixture.py"],
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
  for (let i = 0; i < 150; i++) {
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
try {
  await iniciar();
  assert.equal((await estado()).conversas.length, 0);
  assert.ok(
    await evaluate(
      'Array.from(document.querySelector(".topbar-actions").childNodes).every(n=>n.nodeType!==Node.TEXT_NODE||n.textContent.trim()!=="0")',
    ),
  );
  await click("Criar caderno");
  await fill("Nome do caderno", "Cálculo • laboratório");
  await fill("Objetivo de estudo", "Entender derivadas com exemplos");
  await click("Salvar caderno");
  await wait(
    async () => !(await evaluate('!!document.querySelector("dialog")')),
  );
  assert.equal((await estado()).conversa, null);
  await click("Novo chat");
  await wait(async () => !!(await estado()).conversa);
  const cid = (await estado()).conversa.id;
  await click("Anexar arquivos");
  await wait(async () => {
    const s = await estado();
    return s.anexos[0]?.estado === "pronto";
  });
  await wait(() =>
    evaluate(`!!document.querySelector('[aria-label="Consultar notas.txt"]')`),
  );
  await click("Visualizar notas.txt");
  await wait(async () => (await texto()).includes("Derivada: taxa"));
  await captura("material-claro.png");
  await fecharDialogo();
  await click("Consultar notas.txt");
  await fill(
    "Mensagem",
    "Explique a derivada da função x² − 4x + 3 usando minhas notas.",
  );
  await click("Prévia do envio");
  await wait(async () =>
    (await texto()).includes("Entender derivadas com exemplos"),
  );
  assert.ok((await texto()).includes("[M1] notas.txt"));
  await captura("previa-claro.png");
  await fecharDialogo();
  await click("Enviar mensagem");
  await wait(() =>
    evaluate('document.body.innerText.includes("Enviar com estas fontes")'),
  );
  await click("Enviar com estas fontes");
  await wait(async () => {
    const s = await estado();
    return !s.ocupado && s.mensagens.length === 2;
  });
  await wait(() => evaluate('document.querySelectorAll(".katex").length>=4'));
  assert.ok(await evaluate('!!document.querySelector(".table-scroll table")'));
  await evaluate(
    `document.querySelector(".messages").scrollTo({top:0,behavior:"instant"})`,
  );
  await captura("chat-claro.png");
  await click("Usar tema escuro");
  await wait(() =>
    evaluate('document.documentElement.dataset.theme==="escuro"'),
  );
  await captura("chat-escuro.png");
  await click("Ações do chat aberto");
  await click("Renomear");
  await fill("Título da conversa", "Derivadas — notas e prática");
  await click("Salvar título");
  await wait(
    async () =>
      (await estado()).conversa.titulo === "Derivadas — notas e prática",
  );
  await click("Ações do chat aberto");
  await click("Fixar no topo");
  await wait(async () => !!(await estado()).conversa.fixada);
  await click("Ações do chat aberto");
  await click("Mover para caderno");
  await fill("Caderno de destino", "geral");
  await click("Mover conversa");
  await wait(async () => (await estado()).conversa.caderno_id === null);
  await fill("Mensagem", "Este rascunho deve sobreviver ao reinício.");
  await sleep(450);
  await click("Abrir materiais");
  await wait(() => evaluate('!!document.querySelector(".material-card")'));
  await fill("Buscar materiais", "variação");
  await wait(async () => (await texto()).includes("1 material"));
  await captura("materiais-escuro.png");
  await click("Usar tema claro");
  await wait(() =>
    evaluate('document.documentElement.dataset.theme==="claro"'),
  );
  await captura("materiais-claro.png");
  await click("Usar tema escuro");
  // Teclado: menu, seta, Escape e diálogo com foco contido.
  await click("Ações da conversa Derivadas — notas e prática");
  await cmd("Input.dispatchKeyEvent", {
    type: "keyDown",
    key: "ArrowDown",
    code: "ArrowDown",
    windowsVirtualKeyCode: 40,
  });
  await cmd("Input.dispatchKeyEvent", {
    type: "keyUp",
    key: "ArrowDown",
    code: "ArrowDown",
  });
  assert.equal(
    await evaluate("document.activeElement.textContent"),
    "Desafixar",
  );
  await cmd("Input.dispatchKeyEvent", {
    type: "keyDown",
    key: "Escape",
    code: "Escape",
    windowsVirtualKeyCode: 27,
  });
  await cmd("Input.dispatchKeyEvent", {
    type: "keyUp",
    key: "Escape",
    code: "Escape",
  });
  assert.equal(
    await evaluate('document.activeElement.getAttribute("aria-label")'),
    "Ações da conversa Derivadas — notas e prática",
  );
  await click("Configurações de IA");
  await wait(() => evaluate('!!document.querySelector("dialog[open]")'));
  await click("OpenAIAPI paga por uso");
  await fill("Chave da API", "apenas-um-teste-descartavel");
  assert.equal(
    await evaluate('document.querySelector("input[type=password]").type'),
    "password",
  );
  await fecharDialogo(); // Não grava .env; campo abandonado é descartado.
  await cmd("Emulation.setDeviceMetricsOverride", {
    width: 1000,
    height: 650,
    deviceScaleFactor: 1,
    mobile: false,
  });
  assert.ok(await evaluate("document.documentElement.scrollWidth<=1000"));
  await captura("janela-minima.png");
  await click("Ações da conversa Derivadas — notas e prática");
  await cmd("Input.dispatchKeyEvent", {
    type: "keyDown",
    key: "Escape",
    code: "Escape",
    windowsVirtualKeyCode: 27,
  });
  await click("Derivadas — notas e prática");
  await wait(() => evaluate('!!document.querySelector(".chat-view")'));
  await evaluate(
    'document.querySelector(".messages").scrollTo({top:0,behavior:"instant"})',
  );
  assert.ok(await evaluate("document.documentElement.scrollWidth<=1000"));
  await captura("chat-minimo-escuro.png");
  await click("Usar tema claro");
  await wait(() =>
    evaluate('document.documentElement.dataset.theme==="claro"'),
  );
  await click("Prévia do envio");
  await wait(() => evaluate('!!document.querySelector("dialog[open]")'));
  const limites = await evaluate(
    '(()=>{const r=document.querySelector("dialog").getBoundingClientRect();return {x:r.x,y:r.y,right:r.right,bottom:r.bottom}})()',
  );
  assert.ok(
    limites.x >= 0 &&
      limites.y >= 0 &&
      limites.right <= 1000 &&
      limites.bottom <= 650,
  );
  await fecharDialogo();
  await captura("chat-minimo-claro.png");
  await click("Usar tema escuro");
  await cmd("Emulation.clearDeviceMetricsOverride");
  await click("Recolher barra lateral");
  await wait(() => evaluate('!!document.querySelector(".collapsed")'));
  await captura("lateral-recolhida.png");
  await click("Expandir barra lateral");
  await fechar();
  await iniciar();
  const s = await estado();
  assert.equal(s.conversa.id, cid);
  assert.equal(
    s.conversa.rascunho,
    "Este rascunho deve sobreviver ao reinício.",
  );
  assert.ok(s.conversa.fixada);
  assert.equal(s.mensagens.length, 2);
  assert.ok(s.anexos[0].selecionado);
  assert.equal(s.preferencias.tema, "escuro");
  await fill("Mensagem", "FALHA_SIMULADA");
  await click("Enviar mensagem");
  await wait(() =>
    evaluate('document.body.innerText.includes("Enviar com estas fontes")'),
  );
  await click("Enviar com estas fontes");
  await wait(async () => {
    const s = await estado();
    return !s.ocupado && s.mensagens.at(-1)?.estado === "erro";
  });
  assert.equal((await estado()).conversa.rascunho, "FALHA_SIMULADA");
  await wait(() =>
    evaluate(
      'document.querySelector("textarea[aria-label=Mensagem]").value==="FALHA_SIMULADA"',
    ),
  );
  await click("Ações do chat aberto");
  await click("Arquivar");
  await wait(async () => (await estado()).conversa === null);
  await click("Ver chats arquivados");
  await wait(async () => !!(await estado()).conversa?.arquivada);
  await click("Ações do chat aberto");
  await click("Restaurar");
  await click("Ver chats ativos");
  await wait(
    async () =>
      !!(await estado()).conversa && !(await estado()).conversa.arquivada,
  );
  // Arquivo Office sintético: filtro, páginas de slides, fontes e reinício.
  await writeFile(resolve(pasta, "importar-office"), "1");
  await click("Anexar arquivos");
  await wait(async () =>
    (await estado()).anexos.some(
      (m) => m.nome === "slides.pptx" && m.estado === "parcial",
    ),
  );
  await click("Visualizar slides.pptx");
  await wait(async () => (await texto()).includes("Indução: fórmula"));
  assert.ok((await texto()).includes("Slide 1"));
  await fill("Página do material", "2");
  await wait(async () =>
    (await texto()).includes("Conjuntos no segundo slide"),
  );
  await captura("office-slides-sinteticos.png");
  await fecharDialogo();
  await click("Consultar slides.pptx");
  await fill("Mensagem", "Explique indução usando a fórmula dos slides.");
  await click("Prévia do envio");
  await wait(async () => (await texto()).includes("slides.pptx · slide 1"));
  await fecharDialogo();
  await click("Abrir materiais");
  await fill("Filtrar por tipo", "pptx");
  await wait(async () => (await texto()).includes("1 material"));
  assert.ok((await texto()).includes("slides.pptx"));
  await fechar();
  await iniciar();
  assert.ok(
    (await estado()).anexos.find((m) => m.nome === "slides.pptx")?.selecionado,
  );
  assert.deepEqual(errosPagina, []);
  console.log(
    "E2E OK: janela compilada, cadernos, anexos TXT/PPTX, filtro Office, prévia com slides, IA simulada, menus/teclado, temas, 1000×650, movimentação, arquivo/restauração, fechamento e reinício.",
  );
} catch (e) {
  try {
    if (ws?.readyState === 1) await captura("falha-e2e.png");
  } catch {}
  console.error(e);
  console.error(log);
  process.exitCode = 1;
} finally {
  try {
    await fechar();
  } catch (e) {
    console.error(e);
    process.exitCode = 1;
  }
  await rm(pasta, { recursive: true, force: true });
}
