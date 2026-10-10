import { FormEvent, useEffect, useState } from "react";
import { ApiError, api, Cliente, MovimentacaoEstoque, Produto, Resumo, Usuario, Venda } from "./api";

type Tela = "resumo" | "produtos" | "venda" | "clientes" | "estoque" | "historico";
type CarrinhoItem = { produto: Produto; quantidade: number };

const dinheiro = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const produtoVazio = { nome: "", codigo_barras: "", preco: "", quantidade_estoque: "0" };
const clienteVazio = { nome: "", cpf_cnpj: "", email: "", telefone: "", endereco: "" };
const estoqueVazio = { produto_id: "", quantidade: "", descricao: "" };
const formatarDinheiro = (valor: string) => dinheiro.format(Number(valor));
const erroDaApi = (erro: unknown, padrao: string) => erro instanceof ApiError ? erro.message : padrao;

function Login({ onLogin }: { onLogin: (token: string) => void }) {
  const [username, setUsername] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function entrar(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setEnviando(true); setErro("");
    try { onLogin((await api.login(username, senha)).access_token); }
    catch (error) { setErro(erroDaApi(error, "Não foi possível conectar à API.")); }
    finally { setEnviando(false); }
  }

  return <main className="login-page"><section className="login-intro"><p className="eyebrow">Ponto de Venda</p><h1>Venda clara.<br />Estoque sob controle.</h1><p>Uma interface simples para operar a API que você acabou de construir.</p><div className="login-metric"><strong>FastAPI</strong><span>conectada em tempo real</span></div></section><section className="login-card"><p className="eyebrow">Acesso restrito</p><h2>Entrar no painel</h2><form onSubmit={entrar}><label>Usuário<input value={username} onChange={(event) => setUsername(event.target.value)} required /></label><label>Senha<input type="password" value={senha} onChange={(event) => setSenha(event.target.value)} required /></label>{erro && <p className="alert error">{erro}</p>}<button className="button primary" disabled={enviando}>{enviando ? "Entrando..." : "Entrar"}</button></form></section></main>;
}

function App() {
  const [token, setToken] = useState(() => sessionStorage.getItem("dashboard_token") ?? "");
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [resumo, setResumo] = useState<Resumo | null>(null);
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [estoqueBaixo, setEstoqueBaixo] = useState<Produto[]>([]);
  const [vendas, setVendas] = useState<Venda[]>([]);
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [movimentacoes, setMovimentacoes] = useState<MovimentacaoEstoque[]>([]);
  const [tela, setTela] = useState<Tela>("resumo");
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [busca, setBusca] = useState("");
  const [formProduto, setFormProduto] = useState(produtoVazio);
  const [editandoProduto, setEditandoProduto] = useState<number | null>(null);
  const [formCliente, setFormCliente] = useState(clienteVazio);
  const [editandoCliente, setEditandoCliente] = useState<number | null>(null);
  const [formEstoque, setFormEstoque] = useState(estoqueVazio);
  const [tipoMovimentacao, setTipoMovimentacao] = useState<"entrada" | "ajuste">("entrada");
  const [produtoSelecionado, setProdutoSelecionado] = useState("");
  const [clienteSelecionado, setClienteSelecionado] = useState("");
  const [quantidade, setQuantidade] = useState("1");
  const [carrinho, setCarrinho] = useState<CarrinhoItem[]>([]);
  const administrador = usuario?.perfil === "ADMIN";

  function sair() { sessionStorage.removeItem("dashboard_token"); setToken(""); setUsuario(null); setResumo(null); }

  async function carregarDados(termo = "") {
    if (!token) return;
    setCarregando(true); setErro("");
    try {
      const perfil = await api.me(token);
      const [dadosResumo, listaProdutos, baixos, listaVendas, listaClientes, listaMovimentacoes] = await Promise.all([
        perfil.perfil === "ADMIN" ? api.resumo(token) : Promise.resolve(null), api.produtos(token, termo),
        api.estoqueBaixo(token), api.vendas(token), api.clientes(token), api.movimentacoes(token),
      ]);
      setUsuario(perfil); setResumo(dadosResumo); setProdutos(listaProdutos); setEstoqueBaixo(baixos);
      setVendas(listaVendas); setClientes(listaClientes); setMovimentacoes(listaMovimentacoes);
    } catch (error) {
      setErro(erroDaApi(error, "A API não está disponível."));
      if (error instanceof ApiError && error.status === 401) sair();
    } finally { setCarregando(false); }
  }

  useEffect(() => { void carregarDados(); }, [token]);
  useEffect(() => { if (usuario && !administrador && tela === "resumo") setTela("venda"); }, [usuario, administrador, tela]);

  function entrar(novoToken: string) { sessionStorage.setItem("dashboard_token", novoToken); setToken(novoToken); }
  async function pesquisar(event: FormEvent<HTMLFormElement>) { event.preventDefault(); await carregarDados(busca); }

  async function salvarProduto(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const dados = { nome: formProduto.nome, codigo_barras: formProduto.codigo_barras || null, preco: formProduto.preco, quantidade_estoque: Number(formProduto.quantidade_estoque) };
    try { if (editandoProduto) await api.atualizarProduto(token, editandoProduto, dados); else await api.criarProduto(token, dados); setFormProduto(produtoVazio); setEditandoProduto(null); await carregarDados(busca); }
    catch (error) { setErro(erroDaApi(error, "Não foi possível salvar o produto.")); }
  }

  async function excluirProduto(id: number) {
    if (!window.confirm("Excluir este produto?")) return;
    try { await api.excluirProduto(token, id); await carregarDados(busca); }
    catch (error) { setErro(erroDaApi(error, "Não foi possível excluir o produto.")); }
  }

  async function salvarCliente(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const dados = { nome: formCliente.nome, cpf_cnpj: formCliente.cpf_cnpj || null, email: formCliente.email || null, telefone: formCliente.telefone || null, endereco: formCliente.endereco || null };
    try { if (editandoCliente) await api.atualizarCliente(token, editandoCliente, dados); else await api.criarCliente(token, dados); setFormCliente(clienteVazio); setEditandoCliente(null); await carregarDados(); }
    catch (error) { setErro(erroDaApi(error, "Não foi possível salvar o cliente.")); }
  }

  async function registrarMovimentacao(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const dados = { produto_id: Number(formEstoque.produto_id), quantidade: Number(formEstoque.quantidade), descricao: formEstoque.descricao };
    try {
      if (tipoMovimentacao === "entrada") await api.entradaEstoque(token, dados);
      else await api.ajusteEstoque(token, { ...dados, descricao: dados.descricao || "Ajuste manual de estoque" });
      setFormEstoque(estoqueVazio); await carregarDados();
    } catch (error) { setErro(erroDaApi(error, "Não foi possível registrar a movimentação.")); }
  }

  function adicionarAoCarrinho() {
    const produto = produtos.find((item) => item.id === Number(produtoSelecionado)); const total = Number(quantidade);
    if (!produto || !Number.isInteger(total) || total < 1) return;
    setCarrinho((atual) => { const existente = atual.find((item) => item.produto.id === produto.id); return existente ? atual.map((item) => item.produto.id === produto.id ? { ...item, quantidade: item.quantidade + total } : item) : [...atual, { produto, quantidade: total }]; });
    setProdutoSelecionado(""); setQuantidade("1");
  }

  async function finalizarVenda() {
    if (!carrinho.length) return;
    try { await api.registrarVenda(token, carrinho.map((item) => ({ produto_id: item.produto.id, quantidade: item.quantidade })), clienteSelecionado ? Number(clienteSelecionado) : undefined); setCarrinho([]); setClienteSelecionado(""); setTela("historico"); await carregarDados(); }
    catch (error) { setErro(erroDaApi(error, "Não foi possível registrar a venda.")); }
  }

  async function cancelarVenda(venda: Venda) {
    const motivo = window.prompt(`Cancelar a venda #${venda.id}? Informe o motivo:`);
    if (!motivo) return;
    try { await api.cancelarVenda(token, venda.id, motivo); await carregarDados(); }
    catch (error) { setErro(erroDaApi(error, "Não foi possível cancelar a venda.")); }
  }

  if (!token) return <Login onLogin={entrar} />;
  const totalCarrinho = carrinho.reduce((total, item) => total + Number(item.produto.preco) * item.quantidade, 0);
  const navegacao: [Tela, string][] = [...(administrador ? [["resumo", "Visão geral"] as [Tela, string]] : []), ["produtos", "Produtos"], ["venda", "Nova venda"], ["clientes", "Clientes"], ["estoque", "Estoque"], ["historico", "Histórico"]];
  const titulos: Record<Tela, string> = { resumo: "Bom trabalho, vamos acompanhar.", produtos: "Catálogo de produtos", venda: "Registrar nova venda", clientes: "Clientes", estoque: "Movimentações de estoque", historico: "Histórico de vendas" };

  return <div className="app-shell"><aside className="sidebar"><div className="brand"><span>PV</span><strong>Mercado<br />Clareira</strong></div><nav>{navegacao.map(([id, nome]) => <button key={id} className={tela === id ? "nav-item active" : "nav-item"} onClick={() => setTela(id)}>{nome}</button>)}</nav><div className="sidebar-user"><span>{usuario?.username.slice(0, 1).toUpperCase()}</span><div><strong>{usuario?.username}</strong><small>{administrador ? "Administrador" : "Operador"}</small><button onClick={sair}>Sair</button></div></div></aside><main className="content"><header className="page-header"><div><p className="eyebrow">Operação diária</p><h1>{titulos[tela]}</h1></div><button className="button outline" onClick={() => void carregarDados(busca)}>{carregando ? "Atualizando..." : "Atualizar"}</button></header>{erro && <p className="alert error">{erro}<button onClick={() => setErro("")}>Fechar</button></p>}

    {tela === "resumo" && administrador && resumo && <section className="screen"><div className="metric-grid"><article><span>Faturamento total</span><strong>{formatarDinheiro(resumo.faturamento_total)}</strong><small>{resumo.total_vendas} vendas concluídas</small></article><article><span>Faturamento hoje</span><strong>{formatarDinheiro(resumo.faturamento_hoje)}</strong><small>{resumo.vendas_hoje} vendas hoje</small></article><article><span>Produtos ativos</span><strong>{resumo.total_produtos}</strong><small>no catálogo</small></article><article className="warning"><span>Estoque baixo</span><strong>{resumo.produtos_estoque_baixo}</strong><small>itens precisam de atenção</small></article></div><section className="panel"><div className="panel-heading"><div><p className="eyebrow">Atenção</p><h2>Estoque baixo</h2></div><button className="text-button" onClick={() => setTela("produtos")}>Ver produtos</button></div><div className="low-list">{estoqueBaixo.length ? estoqueBaixo.map((produto) => <div key={produto.id}><strong>{produto.nome}</strong><span>{produto.quantidade_estoque} un.</span></div>) : <p>Nenhum produto abaixo do limite.</p>}</div></section></section>}

    {tela === "produtos" && <section className="screen products-layout">{administrador && <section className="panel form-panel"><p className="eyebrow">{editandoProduto ? "Editar produto" : "Novo produto"}</p><h2>{editandoProduto ? "Atualize o cadastro" : "Adicionar ao catálogo"}</h2><form onSubmit={salvarProduto} className="product-form"><label>Nome<input value={formProduto.nome} onChange={(event) => setFormProduto({ ...formProduto, nome: event.target.value })} required /></label><label>Código de barras<input value={formProduto.codigo_barras} onChange={(event) => setFormProduto({ ...formProduto, codigo_barras: event.target.value })} /></label><div className="form-row"><label>Preço<input type="number" step="0.01" min="0.01" value={formProduto.preco} onChange={(event) => setFormProduto({ ...formProduto, preco: event.target.value })} required /></label><label>Estoque<input type="number" min="0" value={formProduto.quantidade_estoque} onChange={(event) => setFormProduto({ ...formProduto, quantidade_estoque: event.target.value })} required /></label></div><div className="button-row"><button className="button primary">{editandoProduto ? "Salvar" : "Cadastrar"}</button>{editandoProduto && <button type="button" className="button outline" onClick={() => { setEditandoProduto(null); setFormProduto(produtoVazio); }}>Cancelar</button>}</div></form></section>}<section className="panel table-panel"><div className="panel-heading"><div><p className="eyebrow">Catálogo</p><h2>Produtos</h2></div><form className="search" onSubmit={pesquisar}><input placeholder="Buscar por nome" value={busca} onChange={(event) => setBusca(event.target.value)} /><button>Buscar</button></form></div><div className="table-wrap"><table><thead><tr><th>Produto</th><th>Preço</th><th>Estoque</th>{administrador && <th />}</tr></thead><tbody>{produtos.map((produto) => <tr key={produto.id}><td><strong>{produto.nome}</strong><small>{produto.codigo_barras ?? "Sem código"}</small></td><td>{formatarDinheiro(produto.preco)}</td><td><span className={produto.quantidade_estoque <= 5 ? "stock low" : "stock"}>{produto.quantidade_estoque} un.</span></td>{administrador && <td className="actions"><button onClick={() => { setEditandoProduto(produto.id); setFormProduto({ nome: produto.nome, codigo_barras: produto.codigo_barras ?? "", preco: produto.preco, quantidade_estoque: String(produto.quantidade_estoque) }); }}>Editar</button><button className="danger" onClick={() => void excluirProduto(produto.id)}>Excluir</button></td>}</tr>)}</tbody></table></div></section></section>}

    {tela === "venda" && <section className="screen sale-layout"><section className="panel sale-builder"><p className="eyebrow">Caixa</p><h2>Monte a venda</h2><div className="sale-client"><label>Cliente (opcional)<select value={clienteSelecionado} onChange={(event) => setClienteSelecionado(event.target.value)}><option value="">Venda sem cliente</option>{clientes.map((cliente) => <option key={cliente.id} value={cliente.id}>{cliente.nome}{cliente.cpf_cnpj ? ` · ${cliente.cpf_cnpj}` : ""}</option>)}</select></label><button className="text-button" onClick={() => setTela("clientes")}>Cadastrar cliente</button></div><div className="add-line"><label>Produto<select value={produtoSelecionado} onChange={(event) => setProdutoSelecionado(event.target.value)}><option value="">Selecione</option>{produtos.filter((produto) => produto.quantidade_estoque > 0).map((produto) => <option key={produto.id} value={produto.id}>{produto.nome} · {produto.quantidade_estoque} un.</option>)}</select></label><label>Quantidade<input type="number" min="1" value={quantidade} onChange={(event) => setQuantidade(event.target.value)} /></label><button className="button outline" onClick={adicionarAoCarrinho}>Adicionar</button></div><div className="cart">{carrinho.length ? carrinho.map((item) => <div key={item.produto.id}><div><strong>{item.produto.nome}</strong><span>{item.quantidade} x {formatarDinheiro(item.produto.preco)}</span></div><strong>{formatarDinheiro(String(Number(item.produto.preco) * item.quantidade))}</strong><button onClick={() => setCarrinho(carrinho.filter((atual) => atual.produto.id !== item.produto.id))}>Remover</button></div>) : <p>Adicione produtos para iniciar uma venda.</p>}</div></section><aside className="sale-total"><p className="eyebrow">Total</p><strong>{formatarDinheiro(String(totalCarrinho))}</strong><span>{carrinho.length} item(ns)</span><button className="button primary" onClick={() => void finalizarVenda()} disabled={!carrinho.length}>Finalizar venda</button></aside></section>}

    {tela === "clientes" && <section className="screen products-layout"><section className="panel form-panel"><p className="eyebrow">{editandoCliente ? "Editar cliente" : "Novo cliente"}</p><h2>{editandoCliente ? "Atualize os dados" : "Cadastrar cliente"}</h2><form onSubmit={salvarCliente} className="product-form"><label>Nome<input value={formCliente.nome} onChange={(event) => setFormCliente({ ...formCliente, nome: event.target.value })} required /></label><label>CPF ou CNPJ<input value={formCliente.cpf_cnpj} onChange={(event) => setFormCliente({ ...formCliente, cpf_cnpj: event.target.value })} /></label><label>E-mail<input type="email" value={formCliente.email} onChange={(event) => setFormCliente({ ...formCliente, email: event.target.value })} /></label><label>Telefone<input value={formCliente.telefone} onChange={(event) => setFormCliente({ ...formCliente, telefone: event.target.value })} /></label><label>Endereço<input value={formCliente.endereco} onChange={(event) => setFormCliente({ ...formCliente, endereco: event.target.value })} /></label><div className="button-row"><button className="button primary">{editandoCliente ? "Salvar" : "Cadastrar"}</button>{editandoCliente && <button type="button" className="button outline" onClick={() => { setEditandoCliente(null); setFormCliente(clienteVazio); }}>Cancelar</button>}</div></form></section><section className="panel table-panel"><div className="panel-heading"><div><p className="eyebrow">Base de clientes</p><h2>Clientes cadastrados</h2></div><span>{clientes.length} clientes</span></div><div className="table-wrap"><table><thead><tr><th>Cliente</th><th>Documento</th><th>Contato</th><th /></tr></thead><tbody>{clientes.map((cliente) => <tr key={cliente.id}><td><strong>{cliente.nome}</strong><small>{cliente.endereco ?? "Sem endereço"}</small></td><td>{cliente.cpf_cnpj ?? "Não informado"}</td><td>{cliente.email ?? cliente.telefone ?? "Não informado"}</td><td className="actions"><button onClick={() => { setEditandoCliente(cliente.id); setFormCliente({ nome: cliente.nome, cpf_cnpj: cliente.cpf_cnpj ?? "", email: cliente.email ?? "", telefone: cliente.telefone ?? "", endereco: cliente.endereco ?? "" }); }}>Editar</button></td></tr>)}</tbody></table></div></section></section>}

    {tela === "estoque" && <section className="screen products-layout">{administrador && <section className="panel form-panel"><p className="eyebrow">Controle de saldo</p><h2>Registrar movimentação</h2><div className="tabs"><button className={tipoMovimentacao === "entrada" ? "active" : ""} onClick={() => setTipoMovimentacao("entrada")}>Entrada</button><button className={tipoMovimentacao === "ajuste" ? "active" : ""} onClick={() => setTipoMovimentacao("ajuste")}>Ajuste</button></div><form onSubmit={registrarMovimentacao} className="product-form"><label>Produto<select value={formEstoque.produto_id} onChange={(event) => setFormEstoque({ ...formEstoque, produto_id: event.target.value })} required><option value="">Selecione</option>{produtos.map((produto) => <option key={produto.id} value={produto.id}>{produto.nome}</option>)}</select></label><label>{tipoMovimentacao === "entrada" ? "Quantidade recebida" : "Variação de saldo (+ ou -)"}<input type="number" min={tipoMovimentacao === "entrada" ? "1" : undefined} value={formEstoque.quantidade} onChange={(event) => setFormEstoque({ ...formEstoque, quantidade: event.target.value })} required /></label><label>Descrição {tipoMovimentacao === "ajuste" ? "(obrigatória)" : "(opcional)"}<input value={formEstoque.descricao} onChange={(event) => setFormEstoque({ ...formEstoque, descricao: event.target.value })} required={tipoMovimentacao === "ajuste"} /></label><button className="button primary">Registrar {tipoMovimentacao}</button></form></section>}<section className="panel table-panel"><div className="panel-heading"><div><p className="eyebrow">Auditoria</p><h2>Últimas movimentações</h2></div><span>{movimentacoes.length} registros</span></div><div className="table-wrap"><table><thead><tr><th>Data</th><th>Produto</th><th>Tipo</th><th>Quantidade</th><th>Descrição</th></tr></thead><tbody>{movimentacoes.map((movimento) => { const produto = produtos.find((item) => item.id === movimento.produto_id); return <tr key={movimento.id}><td>{new Date(movimento.data).toLocaleString("pt-BR")}</td><td>{produto?.nome ?? `Produto #${movimento.produto_id}`}</td><td><span className="movement-type">{movimento.tipo.replace("_", " ")}</span></td><td className={movimento.quantidade < 0 || movimento.tipo === "SAIDA" ? "negative" : "positive"}>{movimento.tipo === "SAIDA" ? "-" : movimento.quantidade > 0 ? "+" : ""}{movimento.quantidade}</td><td>{movimento.descricao ?? movimento.origem}</td></tr>; })}</tbody></table></div></section></section>}

    {tela === "historico" && <section className="screen panel history"><div className="panel-heading"><div><p className="eyebrow">Registros</p><h2>Últimas vendas</h2></div><span>{vendas.length} vendas</span></div>{vendas.length ? vendas.map((venda) => <article key={venda.id} className={`sale-row ${venda.status === "CANCELADA" ? "cancelled" : ""}`}><div><strong>Venda #{venda.id}</strong><span>{new Date(venda.data).toLocaleString("pt-BR")}</span><small className="sale-status">{venda.status === "CANCELADA" ? "Cancelada" : "Concluída"}</small></div><div className="sale-items">{venda.itens.map((item) => <span key={item.id}>{item.quantidade}x {item.produto_nome}</span>)}{venda.motivo_cancelamento && <small>Motivo: {venda.motivo_cancelamento}</small>}</div><strong>{formatarDinheiro(venda.valor_total)}</strong>{venda.status === "CONCLUIDA" && <button className="text-button danger" onClick={() => void cancelarVenda(venda)}>Cancelar</button>}</article>) : <p>Nenhuma venda registrada ainda.</p>}</section>}
  </main></div>;
}

export default App;
