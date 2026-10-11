// Preserva as licencas dos pacotes distribuidos nos assets compilados.
import {
  readFileSync,
  writeFileSync,
  existsSync,
  realpathSync,
  readdirSync,
} from "node:fs";
import { dirname, resolve, join } from "node:path";
import { fileURLToPath } from "node:url";
const raiz = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const manifesto = JSON.parse(readFileSync(join(raiz, "package.json"), "utf8"));
function localizar(nome, inicio) {
  let pasta = inicio;
  while (true) {
    const candidato = join(pasta, "node_modules", nome);
    if (existsSync(join(candidato, "package.json")))
      return realpathSync(candidato);
    const acima = dirname(pasta);
    if (acima === pasta) throw new Error(`Pacote nao encontrado: ${nome}`);
    pasta = acima;
  }
}
const vistos = new Set(),
  licencas = [];
function visitar(pasta) {
  if (vistos.has(pasta)) return;
  vistos.add(pasta);
  const pkg = JSON.parse(readFileSync(join(pasta, "package.json"), "utf8"));
  const textos = readdirSync(pasta)
    .filter((n) => /^licen[cs]e(?:[.-].*)?$/i.test(n))
    .map((n) => readFileSync(join(pasta, n), "utf8"));
  if (!textos.length) {
    const extra = join(
      raiz,
      "licencas",
      pkg.name.replaceAll("/", "_") + ".txt",
    );
    if (existsSync(extra)) textos.push(readFileSync(extra, "utf8"));
    else throw new Error(`Confira a licenca de ${pkg.name}`);
  }
  licencas.push({
    nome: `${pkg.name} ${pkg.version}`,
    texto: textos.join("\n\n"),
  });
  for (const nome of Object.keys(pkg.dependencies || {}))
    visitar(localizar(nome, pasta));
}
for (const nome of Object.keys(manifesto.dependencies))
  visitar(localizar(nome, raiz));
licencas.sort((a, b) => a.nome.localeCompare(b.nome));
writeFileSync(
  join(raiz, "../tutor_calculo/web/THIRD_PARTY_NOTICES.txt"),
  "CadernoMat — bibliotecas e fontes locais\nGerado por frontend/scripts/licencas.mjs.\n\n" +
    licencas
      .map((l) => `${l.nome}\n${"=".repeat(72)}\n${l.texto}`)
      .join("\n\n"),
);
console.log(`Licencas incluidas: ${licencas.length} pacotes.`);
