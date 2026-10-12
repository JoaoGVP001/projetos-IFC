import { useState } from "react";
import { Check, CheckCircle2, ExternalLink, Sigma } from "lucide-react";
import { api } from "./bridge";
import type { Config, DiagnosticoLocal } from "./model";
import { Button, Field, Badge } from "./ui";

export const nomeProvedor = (p: string) =>
  ({
    ollama: "IA local · Ollama",
    gemini: "Gemini",
    openai: "OpenAI",
    matematica: "Ferramenta local",
  })[p] || p;

export function ConfigForm({
  config,
  save,
  busy,
  notify,
  chat,
}: {
  config: Config;
  save: (d: Record<string, unknown>) => Promise<boolean>;
  busy: boolean;
  notify: (m: string) => void;
  chat: boolean;
}) {
  const initial = config.local || config.provedores.ollama;
  const [provider, setProvider] = useState(config.provedor);
  const [model, setModel] = useState(
    config.modelo || config.provedores[config.provedor].modelo,
  );
  const [key, setKey] = useState("");
  const [scope, setScope] = useState(chat ? "chat" : "padrao");
  const [url, setUrl] = useState(initial?.url || "http://127.0.0.1:11434");
  const [context, setContext] = useState(initial?.contexto || 4096);
  const [profile, setProfile] = useState(initial?.perfil || "legado");
  const [timeout, setTimeoutLocal] = useState(initial?.timeout || 180);
  const [diagnostic, setDiagnostic] = useState<DiagnosticoLocal | null>(null);
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState("");
  const escolher = (p: string) => {
    setProvider(p);
    setModel(config.provedores[p].modelo);
    setKey("");
    setDiagnostic(null);
    setError("");
  };
  const abrir = (u: string) =>
    void api("abrir_link", { url: u }).catch((e) => notify(e.message));
  const diagnosticar = async (iniciar = false) => {
    setTesting(true);
    setError("");
    try {
      const args = {
        modelo: model,
        url,
        contexto: context,
        timeout,
        perfil: profile,
      };
      if (iniciar) await api("ollama_iniciar", args);
      setDiagnostic(await api<DiagnosticoLocal>("ollama_diagnostico", args));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setTesting(false);
    }
  };
  return (
    <form
      onSubmit={async (e) => {
        e.preventDefault();
        try {
          await save(
            provider === "ollama"
              ? {
                  provedor: provider,
                  modelo: model,
                  escopo: scope,
                  url,
                  contexto: context,
                  timeout,
                  perfil: profile,
                }
              : {
                  provedor: provider,
                  modelo: model,
                  chave: key,
                  escopo: scope,
                },
          );
        } finally {
          setKey("");
        }
      }}
    >
      <div className="provider-options">
        {["ollama", "gemini", "openai"].map((p) => (
          <button
            type="button"
            aria-label={nomeProvedor(p)}
            key={p}
            className={`provider-option ${provider === p ? "active" : ""}`}
            onClick={() => escolher(p)}
          >
            <span className="provider-symbol">
              <Sigma size={21} />
            </span>
            <strong>{nomeProvedor(p)}</strong>
            <small>
              {p === "ollama"
                ? "Neste computador · sem chave"
                : p === "gemini"
                  ? "Cota gratuita ou paga"
                  : "API paga por uso"}
            </small>
            {provider === p && <CheckCircle2 size={17} />}
          </button>
        ))}
      </div>
      <Field
        label="Aplicar configuração"
        hint="Cada resposta registra o provedor e o modelo usados. Alterar esta escolha preserva as mensagens antigas."
      >
        <select value={scope} onChange={(e) => setScope(e.target.value)}>
          {chat && <option value="chat">Somente esta conversa</option>}
          <option value="padrao">
            Padrão para conversas que herdam a configuração
          </option>
          {chat && (
            <option value="herdar">
              Esta conversa deve usar o padrão (
              {nomeProvedor(config.padrao || config.provedor)})
            </option>
          )}
        </select>
      </Field>
      {scope !== "herdar" && (
        <>
          <Field
            label="Modelo"
            hint={
              provider === "ollama"
                ? "Use uma tag instalada com pesos locais. Não há download automático."
                : undefined
            }
          >
            <input
              required
              maxLength={100}
              value={model}
              onChange={(e) => {
                setModel(e.target.value);
                setDiagnostic(null);
              }}
            />
          </Field>
          {provider === "ollama" ? (
            <>
              <Field
                label="Endereço do Ollama"
                hint="Somente HTTP em 127.0.0.1, sem credenciais ou redirecionamentos."
              >
                <input
                  required
                  value={url}
                  onChange={(e) => {
                    setUrl(e.target.value);
                    setDiagnostic(null);
                  }}
                  maxLength={100}
                />
              </Field>
              <div className="form-grid">
                <Field label="Contexto local">
                  <select
                    value={context}
                    onChange={(e) => setContext(Number(e.target.value))}
                  >
                    <option value={2048}>2.048 tokens · menor consumo</option>
                    <option value={4096}>
                      4.096 tokens · perfil do notebook
                    </option>
                  </select>
                </Field>
                <Field label="Perfil de resposta">
                  <select
                    aria-label="Perfil de resposta"
                    value={profile}
                    onChange={(e) => {
                      setProfile(e.target.value);
                      if (e.target.value === "completo") setContext(4096);
                      setTimeoutLocal(
                        (
                          {
                            rapido: 180,
                            estudo: 240,
                            completo: 360,
                            legado: 180,
                          } as Record<string, number>
                        )[e.target.value],
                      );
                    }}
                  >
                    <option value="legado">Configuração anterior</option>
                    <option value="rapido">Rápido no notebook</option>
                    <option value="estudo">Estudo</option>
                    <option value="completo">
                      Completo · pode demorar em CPU
                    </option>
                  </select>
                </Field>
                <Field label="Tempo limite (segundos)">
                  <input
                    type="number"
                    required
                    min={30}
                    max={600}
                    value={timeout}
                    onChange={(e) => setTimeoutLocal(Number(e.target.value))}
                  />
                </Field>
              </div>
              <p className="hint">
                Pergunta, histórico recente e trechos selecionados vão apenas ao
                servidor local. Imagens e PDFs entram pelo texto já extraído;
                visão ainda não está integrada. Sem troca automática para nuvem.
              </p>
              <div className="local-actions">
                <Button
                  disabled={testing || busy}
                  onClick={() => void diagnosticar()}
                >
                  {testing ? "Verificando…" : "Testar conexão e listar modelos"}
                </Button>
                <Button
                  disabled={testing || busy}
                  onClick={() => void diagnosticar(true)}
                >
                  Iniciar runtime do piloto
                </Button>
              </div>
              {error && (
                <p role="alert" className="activity-warning">
                  {error}
                </p>
              )}
              {diagnostic && (
                <div className="local-diagnostic" role="status">
                  <Badge kind="success">
                    Ollama {diagnostic.versao} conectado
                  </Badge>
                  <p className="hint">
                    {diagnostic.modelo_disponivel
                      ? `Modelo de texto disponível${diagnostic.carregado ? " e carregado" : " · será carregado na primeira consulta"}.`
                      : diagnostic.aviso}
                  </p>
                  <p>
                    Execução atual:{" "}
                    {diagnostic.dispositivo?.estado === "nao_carregado"
                      ? "nenhum modelo carregado agora"
                      : diagnostic.dispositivo?.processador || "desconhecida"}
                    . Contexto observado:{" "}
                    {diagnostic.dispositivo?.contexto ?? "não informado"}.
                  </p>
                  <p>
                    RAM disponível:{" "}
                    {diagnostic.memoria?.ram_disponivel == null
                      ? "não medida"
                      : (diagnostic.memoria.ram_disponivel / 2 ** 30).toFixed(
                          1,
                        ) + " GiB"}{" "}
                    · swap usada:{" "}
                    {diagnostic.memoria?.swap_usada == null
                      ? "não medida"
                      : (diagnostic.memoria.swap_usada / 2 ** 30).toFixed(1) +
                        " GiB"}
                    .
                  </p>
                  <Field label="Modelos instalados">
                    <select
                      value={
                        diagnostic.modelos.some((m) => m.name === model)
                          ? model
                          : ""
                      }
                      onChange={(e) => {
                        setModel(e.target.value);
                        setDiagnostic(null);
                      }}
                    >
                      <option value="" disabled>
                        Escolha um modelo local
                      </option>
                      {diagnostic.modelos.map((m) => (
                        <option key={m.name} value={m.name}>
                          {m.name} · {(m.size / 1e9).toFixed(2)} GB ·{" "}
                          {m.details?.quantization_level}
                        </option>
                      ))}
                    </select>
                  </Field>
                  <small>
                    Capacidades anunciadas pelo modelo:{" "}
                    {diagnostic.capacidades.join(", ") || "não consultadas"}.
                    Nesta entrega: texto, streaming e JSON; não executa
                    ferramentas sugeridas pelo modelo.
                  </small>
                </div>
              )}
              <p className="hint">
                A qualidade matemática continua experimental. Revise o
                raciocínio e os gabaritos. A primeira resposta pode demorar
                enquanto o modelo carrega.
              </p>
            </>
          ) : (
            <>
              <Field
                label="Chave da API"
                hint={
                  config.provedores[provider].configurada
                    ? "Já existe uma chave salva. Deixe vazio para reutilizá-la."
                    : "Configure uma chave pessoal desse provedor."
                }
              >
                <input
                  type="password"
                  autoComplete="off"
                  maxLength={500}
                  value={key}
                  onChange={(e) => setKey(e.target.value)}
                  placeholder="Cole sua chave aqui"
                />
              </Field>
              <p className="hint">
                A chave fica no Python, no arquivo local protegido. Salvar não
                testa acesso nem ativa faturamento. A assinatura do ChatGPT é
                separada da API.
              </p>
              <div className="config-links">
                <button
                  type="button"
                  onClick={() =>
                    abrir(
                      provider === "gemini"
                        ? "https://aistudio.google.com/api-keys"
                        : "https://platform.openai.com/api-keys",
                    )
                  }
                >
                  Criar ou conferir chave <ExternalLink size={13} />
                </button>
                <button
                  type="button"
                  onClick={() =>
                    abrir(
                      provider === "gemini"
                        ? "https://ai.google.dev/gemini-api/docs/pricing"
                        : "https://openai.com/api/pricing/",
                    )
                  }
                >
                  Cotas e preços <ExternalLink size={13} />
                </button>
              </div>
            </>
          )}
        </>
      )}
      <div className="form-actions">
        <Button
          type="submit"
          variant="primary"
          disabled={busy || testing}
          icon={Check}
        >
          Salvar configuração
        </Button>
      </div>
    </form>
  );
}
