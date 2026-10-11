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
const capturas = resolve(raiz, "docs/screenshots");
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
  await evaluate(
    'document.querySelector(".activities-view")?.scrollTo({top:0,behavior:"instant"}); document.activeElement?.blur()',
  );
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
async function escolha(n) {
  await evaluate(
    `document.querySelectorAll('.practice-answers input')[${n}].click()`,
  );
}
async function conteudoDaPagina(s) {
  await wait(async () => (await texto()).includes(s));
}
try {
  await iniciar();
  await click("Abrir atividades");
  await click("Criar atividade");
  await fill("Título da atividade", "Funções · prática de revisão");
  await fill(
    "Objetivo de aprendizagem",
    "Conferir derivadas e explicar conceitos",
  );
  await fill("Assuntos", "Funções e derivadas");
  await fill("Formato do exercício", "numerica");
  await fill("Enunciado", "Para $f(x)=x^2-4x+3$, calcule $f(2)$.");
  await fill("Resposta numérica esperada", "-1");
  await fill("Tolerância absoluta", "0");
  await fill("Explicação da solução (opcional)", "$f(2)=4-8+3=-1$.");
  await click("Adicionar exercício");
  await fill("Formato do exercício", "escolha");
  await fill("Enunciado", "Qual é a derivada $f'(x)$?");
  await fill("Alternativa 1", "$2x-4$");
  await fill("Alternativa 2", "$2x+4$");
  await click("Alternativa 1 correta");
  await click("Adicionar exercício");
  await fill("Formato do exercício", "vf");
  await fill("Enunciado", "O mínimo da função ocorre em $x=2$.");
  await fill("Gabarito", "true");
  await click("Adicionar exercício");
  await fill("Enunciado", "Explique o que significa a derivada.");
  await captura("atividades-editor-claro.png");
  await click("Usar tema escuro");
  await captura("atividades-editor-escuro.png");
  await click("Usar tema claro");
  await click("Salvar atividade");
  await conteudoDaPagina("Começar ou continuar");
  const aid = (await rpc("atividades")).itens[0].id;
  assert.equal((await rpc("atividade_obter", { id: aid })).versao, 1);
  await click("Começar ou continuar");
  await conteudoDaPagina("Exercício 1 de 4");
  await fill("Sua resposta", "-1");
  await click("Próximo exercício");
  await conteudoDaPagina("Exercício 2 de 4");
  await escolha(0);
  await click("Próximo exercício");
  await conteudoDaPagina("Exercício 3 de 4");
  await escolha(1);
  const tid = (await estado()).estudo.tentativa;
  await wait(() =>
    evaluate('document.querySelectorAll(".practice-answers input")[1].checked'),
  );
  // Fecha antes do debounce: callback desktop deve salvar a última escolha.
  await fechar();
  await iniciar();
  await conteudoDaPagina("Exercício 3 de 4");
  let t = await rpc("tentativa_obter", { id: tid });
  assert.equal(t.posicao, 2);
  assert.equal(
    t.respostas[t.snapshot.conteudo.exercicios[2].id].resposta,
    false,
  );
  assert.ok(!("resposta" in t.snapshot.conteudo.exercicios[0]));
  await captura("atividades-pratica-claro.png");
  await click("Usar tema escuro");
  await conteudoDaPagina("Exercício 3 de 4");
  await captura("atividades-pratica-escuro.png");
  await click("Próximo exercício");
  await fill("Sua resposta", "A derivada mede a taxa de variação instantânea.");
  await click("Finalizar tentativa");
  await conteudoDaPagina("Tentativa finalizada");
  t = await rpc("tentativa_obter", { id: tid });
  assert.equal(t.resumo.acertos, 2);
  assert.equal(t.resumo.erros, 1);
  assert.equal(t.resumo.nao_avaliadas, 1);
  await fill("Observação manual", "Rever a ligação entre inclinação e taxa.");
  await click("Salvar revisão manual");
  await conteudoDaPagina("Revisão manual ·");
  await captura("atividades-revisao-escuro.png");
  await click("Usar tema claro");
  await captura("atividades-revisao-claro.png");
  await click("Feedback com IA");
  await click("Conferir dados enviados");
  await conteudoDaPagina("resposta_do_aluno");
  await click("Confirmar consulta à API");
  await conteudoDaPagina("Orientação simulada");
  await fecharDialogo();
  t = await rpc("tentativa_obter", { id: tid });
  assert.equal(t.resumo.objetivas, 3);
  assert.equal(
    t.respostas[t.snapshot.conteudo.exercicios[3].id].feedbacks[0].provedor,
    "gemini",
  );
  await click("Histórico da atividade");
  await click("Nova tentativa");
  await conteudoDaPagina("Exercício 1 de 4");
  const nova = (await estado()).estudo.tentativa;
  assert.notEqual(nova, tid);
  await click("Pedir dica com IA");
  await click("Conferir dados enviados");
  assert.ok(!(await texto()).includes("resposta_esperada"));
  await click("Confirmar consulta à API");
  await conteudoDaPagina("Orientação simulada");
  await fecharDialogo();
  await click("Revelar solução");
  await conteudoDaPagina("revelação registrada");
  assert.equal((await rpc("tentativa_obter", { id: nova })).resumo.solucoes, 1);
  await click("Finalizar tentativa");
  await conteudoDaPagina("4 questão(ões) sem resposta");
  await click("Finalizar mesmo assim");
  await conteudoDaPagina("Tentativa finalizada");
  assert.equal(
    (await rpc("tentativa_obter", { id: nova })).resumo.objetivas,
    0,
  );
  await click("Histórico da atividade");
  await click("Comparar tentativa " + tid);
  await click("Comparar tentativa " + nova);
  await click("Comparar duas tentativas");
  await conteudoDaPagina("Mesma versão");
  await fecharDialogo();
  await captura("atividades-historico-claro.png");
  await click("Usar tema escuro");
  await captura("atividades-historico-escuro.png");
  await click("Editar atividade");
  await fill("Título da atividade", "Funções · versão revisada");
  await fill("Resposta numérica esperada", "42");
  await click("Salvar atividade");
  await conteudoDaPagina("VERSÃO 2");
  t = await rpc("tentativa_obter", { id: tid });
  assert.equal(t.versao, 1);
  assert.equal(t.snapshot.conteudo.exercicios[0].resposta, "-1");
  await click("Todas as atividades");
  await click("Gerar com IA");
  await fill("Assunto para gerar", "Derivadas");
  await fill("Quantidade de exercícios (1–10)", "2");
  await evaluate(
    `Array.from(document.querySelectorAll('.generation-formats label')).find(e=>e.textContent==='Resposta aberta').querySelector('input').click()`,
  );
  await evaluate(
    `Array.from(document.querySelectorAll('.generation-formats label')).find(e=>e.textContent==='Resposta numérica').querySelector('input').click()`,
  );
  await click("Conferir dados enviados");
  await captura("atividades-previa-escuro.png");
  await click("Confirmar consulta à API");
  await conteudoDaPagina("Revisar proposta no editor");
  assert.equal((await rpc("atividades")).total, 1);
  await click("Revisar proposta no editor");
  await conteudoDaPagina("PROPOSTA DE IA");
  await click("Salvar atividade");
  await conteudoDaPagina("Proposta gemini revisada");
  assert.equal((await rpc("atividades")).total, 2);
  await cmd("Emulation.setDeviceMetricsOverride", {
    width: 1000,
    height: 650,
    deviceScaleFactor: 1,
    mobile: false,
  });
  assert.ok(await evaluate("document.documentElement.scrollWidth<=1000"));
  await click("Nova tentativa");
  await conteudoDaPagina("Exercício 1 de 2");
  await captura("atividades-minimo-escuro.png");
  await click("Usar tema claro");
  await captura("atividades-minimo-claro.png");
  await click("Pedir dica com IA");
  await click("Conferir dados enviados");
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
  await click("Pedir ajuda em novo chat");
  await wait(() =>
    evaluate(
      'document.querySelector("textarea[aria-label=Mensagem]")?.value.includes("Me dê uma dica progressiva")',
    ),
  );
  assert.ok((await estado()).conversa.rascunho.includes("Calcule"));
  assert.ok(!(await estado()).conversa.rascunho.includes("resposta_esperada"));
  // Integração real: origem no chat e material escolhido na biblioteca.
  await cmd("Emulation.clearDeviceMetricsOverride");
  await click("Ações do chat aberto");
  await click("Criar atividade deste chat");
  await fill("Título da atividade", "Prática a partir do chat");
  await fill("Enunciado", "Explique a soma apresentada.");
  await click("Salvar atividade");
  await conteudoDaPagina("Origem: Ajuda:");
  const chatSource = (await estado()).conversa.id;
  assert.equal(
    (await rpc("atividades")).itens.find(
      (a) => a.conteudo.titulo === "Prática a partir do chat",
    ).origem_chat,
    chatSource,
  );
  await click("Ajuda: Derivadas · proposta simulada");
  await click("Anexar arquivos");
  await wait(async () => (await estado()).anexos[0]?.estado === "pronto");
  const mid = (await estado()).anexos[0].id;
  await click("Abrir materiais");
  await click("Ações do material notas.txt");
  await click("Criar atividade deste material");
  await fill("Assuntos", "Derivadas");
  await click("Gerar proposta com IA");
  await fill("Quantidade de exercícios (1–10)", "2");
  await evaluate(
    `Array.from(document.querySelectorAll('.generation-formats label')).find(e=>e.textContent==='Resposta aberta').querySelector('input').click()`,
  );
  await evaluate(
    `Array.from(document.querySelectorAll('.generation-formats label')).find(e=>e.textContent==='Resposta numérica').querySelector('input').click()`,
  );
  await click("Conferir dados enviados");
  await conteudoDaPagina("M1 · notas.txt");
  await captura("atividades-previa-claro.png");
  await click("Confirmar consulta à API");
  await conteudoDaPagina("Revisar proposta no editor");
  await click("Revisar proposta no editor");
  await click("Salvar atividade");
  await conteudoDaPagina("Proposta gemini revisada");
  const gerada = (await rpc("atividades")).itens[0];
  const detalhe = await rpc("atividade_obter", { id: gerada.id });
  assert.equal(detalhe.fontes[0].id, mid);
  assert.equal(detalhe.conteudo.exercicios[0].referencias[0].material_id, mid);
  assert.equal((await estado()).anexos.length, 1);
  assert.deepEqual(errosPagina, []);
  console.log(
    "E2E atividades OK: editor manual, 4 formatos, último rascunho/reinício, correção, revisão, histórico/comparação, versões imutáveis, dicas/feedback/geração simulados, ajuda em chat, temas e 1000×650.",
  );
} catch (e) {
  try {
    if (ws?.readyState === 1) await captura("falha-atividades-e2e.png");
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
