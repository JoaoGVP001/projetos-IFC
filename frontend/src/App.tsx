import { FormEvent, useEffect, useState } from "react";
import { ApiError, api, Produto, Resumo, Usuario, Venda } from "./api";

type Tela = "resumo" | "produtos" | "venda" | "historico";
type CarrinhoItem = { produto: Produto; quantidade: number };

const dinheiro = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

const produtoVazio = {
  nome: "",
  codigo_barras: "",
  preco: "",
  quantidade_estoque: "0",
};

function formatarDinheiro(valor: string) {
  return dinheiro.format(Number(valor));
}

function Login({ onLogin }: { onLogin: (token: string) => void }) {
  const [username, setUsername] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function entrar(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setEnviando(true);
    setErro("");
    try {
      const resposta = await api.login(username, senha);
      onLogin(resposta.access_token);
    } catch (error) {
      setErro(error instanceof ApiError ? error.message : "Não foi possível conectar à API.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-intro">
        <p className="eyebrow">Ponto de Venda</p>
        <h1>Venda clara.<br />Estoque sob controle.</h1>
        <p>Uma interface simples para operar a API que você acabou de construir.</p>
        <div className="login-metric"><strong>FastAPI</strong><span>conectada em tempo real</span></div>
      </section>
      <section className="login-card">
        <p className="eyebrow">Acesso restrito</p>
        <h2>Entrar no painel</h2>
        <form onSubmit={entrar}>
          <label>Usuário<input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" required /></label>
          <label>Senha<input type="password" value={senha} onChange={(e) => setSenha(e.target.value)} autoComplete="current-password" required /></label>
          {erro && <p className="alert error">{erro}</p>}
          <button className="button primary" disabled={enviando}>{enviando ? "Entrando..." : "Entrar"}</button>
        </form>
      </section>
    </main>
  );
}

function App() {
  const [token, setToken] = useState(() => sessionStorage.getItem("dashboard_token") ?? "");
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [resumo, setResumo] = useState<Resumo | null>(null);
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [estoqueBaixo, setEstoqueBaixo] = useState<Produto[]>([]);
  const [vendas, setVendas] = useState<Venda[]>([]);
  const [tela, setTela] = useState<Tela>("resumo");
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [busca, setBusca] = useState("");
  const [editando, setEditando] = useState<number | null>(null);
  const [formProduto, setFormProduto] = useState(produtoVazio);
  const [produtoSelecionado, setProdutoSelecionado] = useState("");
  const [quantidade, setQuantidade] = useState("1");
  const [carrinho, setCarrinho] = useState<CarrinhoItem[]>([]);

  async function carregarDados(termo = "") {
    if (!token) return;
    setCarregando(true);
    setErro("");
    try {
      const [perfil, dadosResumo, listaProdutos, baixos, listaVendas] = await Promise.all([
        api.me(token), api.resumo(token), api.produtos(token, termo), api.estoqueBaixo(token), api.vendas(token),
      ]);
      setUsuario(perfil);
      setResumo(dadosResumo);
      setProdutos(listaProdutos);
      setEstoqueBaixo(baixos);
      setVendas(listaVendas);
    } catch (error) {
      const mensagem = error instanceof ApiError ? error.message : "A API não está disponível.";
      setErro(mensagem);
      if (error instanceof ApiError && error.status === 401) sair();
    } finally {
      setCarregando(false);
    }
  }

  useEffect(() => { void carregarDados(); }, [token]);

  function entrar(novoToken: string) {
    sessionStorage.setItem("dashboard_token", novoToken);
    setToken(novoToken);
  }

  function sair() {
    sessionStorage.removeItem("dashboard_token");
    setToken("");
    setUsuario(null);
  }

  async function pesquisar(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await carregarDados(busca);
  }

  async function salvarProduto(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      const dados = {
        nome: formProduto.nome,
        codigo_barras: formProduto.codigo_barras || null,
        preco: formProduto.preco,
        quantidade_estoque: Number(formProduto.quantidade_estoque),
      };
      if (editando) await api.atualizarProduto(token, editando, dados);
      else await api.criarProduto(token, dados);
      setFormProduto(produtoVazio);
      setEditando(null);
      await carregarDados(busca);
    } catch (error) {
      setErro(error instanceof ApiError ? error.message : "Não foi possível salvar o produto.");
    }
  }

  function prepararEdicao(produto: Produto) {
    setEditando(produto.id);
    setFormProduto({
      nome: produto.nome,
      codigo_barras: produto.codigo_barras ?? "",
      preco: produto.preco,
      quantidade_estoque: String(produto.quantidade_estoque),
    });
    setTela("produtos");
  }

  async function excluirProduto(id: number) {
    if (!window.confirm("Excluir este produto?")) return;
    try {
      await api.excluirProduto(token, id);
      await carregarDados(busca);
    } catch (error) {
      setErro(error instanceof ApiError ? error.message : "Não foi possível excluir o produto.");
    }
  }

  function adicionarAoCarrinho() {
    const produto = produtos.find((item) => item.id === Number(produtoSelecionado));
    const total = Number(quantidade);
    if (!produto || !Number.isInteger(total) || total < 1) return;
    setCarrinho((atual) => {
      const existente = atual.find((item) => item.produto.id === produto.id);
      if (existente) return atual.map((item) => item.produto.id === produto.id ? { ...item, quantidade: item.quantidade + total } : item);
      return [...atual, { produto, quantidade: total }];
    });
    setProdutoSelecionado("");
    setQuantidade("1");
  }

  async function finalizarVenda() {
    if (!carrinho.length) return;
    try {
      await api.registrarVenda(token, carrinho.map((item) => ({ produto_id: item.produto.id, quantidade: item.quantidade })));
      setCarrinho([]);
      setTela("historico");
      await carregarDados();
    } catch (error) {
      setErro(error instanceof ApiError ? error.message : "Não foi possível registrar a venda.");
    }
  }

  if (!token) return <Login onLogin={entrar} />;

  const totalCarrinho = carrinho.reduce((total, item) => total + Number(item.produto.preco) * item.quantidade, 0);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span>PV</span><strong>Mercado<br />Clareira</strong></div>
        <nav>
          {([['resumo', 'Visão geral'], ['produtos', 'Produtos'], ['venda', 'Nova venda'], ['historico', 'Histórico']] as [Tela, string][]).map(([id, nome]) => (
            <button key={id} className={tela === id ? "nav-item active" : "nav-item"} onClick={() => setTela(id)}>{nome}</button>
          ))}
        </nav>
        <div className="sidebar-user"><span>{usuario?.username.slice(0, 1).toUpperCase()}</span><div><strong>{usuario?.username}</strong><button onClick={sair}>Sair</button></div></div>
      </aside>

      <main className="content">
        <header className="page-header"><div><p className="eyebrow">Operação diária</p><h1>{tela === "resumo" ? "Bom trabalho, vamos acompanhar." : tela === "produtos" ? "Catálogo de produtos" : tela === "venda" ? "Registrar nova venda" : "Histórico de vendas"}</h1></div><button className="button outline" onClick={() => void carregarDados(busca)}>{carregando ? "Atualizando..." : "Atualizar"}</button></header>
        {erro && <p className="alert error">{erro}<button onClick={() => setErro("")}>Fechar</button></p>}

        {tela === "resumo" && resumo && <section className="screen"><div className="metric-grid">
          <article><span>Faturamento total</span><strong>{formatarDinheiro(resumo.faturamento_total)}</strong><small>{resumo.total_vendas} vendas registradas</small></article>
          <article><span>Faturamento hoje</span><strong>{formatarDinheiro(resumo.faturamento_hoje)}</strong><small>{resumo.vendas_hoje} vendas hoje</small></article>
          <article><span>Produtos ativos</span><strong>{resumo.total_produtos}</strong><small>no catálogo</small></article>
          <article className="warning"><span>Estoque baixo</span><strong>{resumo.produtos_estoque_baixo}</strong><small>itens precisam de atenção</small></article>
        </div><section className="panel"><div className="panel-heading"><div><p className="eyebrow">Atenção</p><h2>Estoque baixo</h2></div><button className="text-button" onClick={() => setTela("produtos")}>Ver produtos</button></div><div className="low-list">{estoqueBaixo.length ? estoqueBaixo.map((produto) => <div key={produto.id}><strong>{produto.nome}</strong><span>{produto.quantidade_estoque} un.</span></div>) : <p>Nenhum produto abaixo do limite.</p>}</div></section></section>}

        {tela === "produtos" && <section className="screen products-layout"><section className="panel form-panel"><p className="eyebrow">{editando ? "Editar produto" : "Novo produto"}</p><h2>{editando ? "Atualize o cadastro" : "Adicionar ao catálogo"}</h2><form onSubmit={salvarProduto} className="product-form"><label>Nome<input value={formProduto.nome} onChange={(e) => setFormProduto({ ...formProduto, nome: e.target.value })} required /></label><label>Código de barras<input value={formProduto.codigo_barras} onChange={(e) => setFormProduto({ ...formProduto, codigo_barras: e.target.value })} /></label><div className="form-row"><label>Preço<input type="number" step="0.01" min="0.01" value={formProduto.preco} onChange={(e) => setFormProduto({ ...formProduto, preco: e.target.value })} required /></label><label>Estoque<input type="number" min="0" value={formProduto.quantidade_estoque} onChange={(e) => setFormProduto({ ...formProduto, quantidade_estoque: e.target.value })} required /></label></div><div className="button-row"><button className="button primary">{editando ? "Salvar" : "Cadastrar"}</button>{editando && <button type="button" className="button outline" onClick={() => { setEditando(null); setFormProduto(produtoVazio); }}>Cancelar</button>}</div></form></section><section className="panel table-panel"><div className="panel-heading"><div><p className="eyebrow">Catálogo</p><h2>Produtos</h2></div><form className="search" onSubmit={pesquisar}><input placeholder="Buscar por nome" value={busca} onChange={(e) => setBusca(e.target.value)} /><button>Buscar</button></form></div><div className="table-wrap"><table><thead><tr><th>Produto</th><th>Preço</th><th>Estoque</th><th /></tr></thead><tbody>{produtos.map((produto) => <tr key={produto.id}><td><strong>{produto.nome}</strong><small>{produto.codigo_barras ?? "Sem código"}</small></td><td>{formatarDinheiro(produto.preco)}</td><td><span className={produto.quantidade_estoque <= 5 ? "stock low" : "stock"}>{produto.quantidade_estoque} un.</span></td><td className="actions"><button onClick={() => prepararEdicao(produto)}>Editar</button><button className="danger" onClick={() => void excluirProduto(produto.id)}>Excluir</button></td></tr>)}</tbody></table></div></section></section>}

        {tela === "venda" && <section className="screen sale-layout"><section className="panel sale-builder"><p className="eyebrow">Caixa</p><h2>Monte a venda</h2><div className="add-line"><label>Produto<select value={produtoSelecionado} onChange={(e) => setProdutoSelecionado(e.target.value)}><option value="">Selecione</option>{produtos.filter((produto) => produto.quantidade_estoque > 0).map((produto) => <option key={produto.id} value={produto.id}>{produto.nome} · {produto.quantidade_estoque} un.</option>)}</select></label><label>Quantidade<input type="number" min="1" value={quantidade} onChange={(e) => setQuantidade(e.target.value)} /></label><button className="button outline" onClick={adicionarAoCarrinho}>Adicionar</button></div><div className="cart">{carrinho.length ? carrinho.map((item) => <div key={item.produto.id}><div><strong>{item.produto.nome}</strong><span>{item.quantidade} x {formatarDinheiro(item.produto.preco)}</span></div><strong>{formatarDinheiro(String(Number(item.produto.preco) * item.quantidade))}</strong><button onClick={() => setCarrinho(carrinho.filter((atual) => atual.produto.id !== item.produto.id))}>Remover</button></div>) : <p>Adicione produtos para iniciar uma venda.</p>}</div></section><aside className="sale-total"><p className="eyebrow">Total</p><strong>{formatarDinheiro(String(totalCarrinho))}</strong><span>{carrinho.length} item(ns)</span><button className="button primary" onClick={() => void finalizarVenda()} disabled={!carrinho.length}>Finalizar venda</button></aside></section>}

        {tela === "historico" && <section className="screen panel history"><div className="panel-heading"><div><p className="eyebrow">Registros</p><h2>Últimas vendas</h2></div><span>{vendas.length} vendas</span></div>{vendas.length ? vendas.map((venda) => <article key={venda.id} className="sale-row"><div><strong>Venda #{venda.id}</strong><span>{new Date(venda.data).toLocaleString("pt-BR")}</span></div><div className="sale-items">{venda.itens.map((item) => <span key={item.id}>{item.quantidade}x {item.produto_nome}</span>)}</div><strong>{formatarDinheiro(venda.valor_total)}</strong></article>) : <p>Nenhuma venda registrada ainda.</p>}</section>}
      </main>
    </div>
  );
}

export default App;
