const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type Usuario = {
  id: number;
  username: string;
  email: string;
  ativo: boolean;
};

export type Produto = {
  id: number;
  nome: string;
  codigo_barras: string | null;
  preco: string;
  quantidade_estoque: number;
};

export type ItemVenda = {
  id: number;
  produto_id: number;
  produto_nome: string;
  quantidade: number;
  preco_unitario: string;
  subtotal: string;
};

export type Venda = {
  id: number;
  usuario_id: number;
  data: string;
  valor_total: string;
  itens: ItemVenda[];
};

export type Resumo = {
  total_produtos: number;
  total_vendas: number;
  faturamento_total: string;
  produtos_estoque_baixo: number;
  vendas_hoje: number;
  faturamento_hoje: string;
};

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request<T>(
  path: string,
  token?: string,
  init: RequestInit = {},
): Promise<T> {
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(response.status, body?.detail ?? "Não foi possível concluir a operação.");
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export async function login(username: string, password: string) {
  const body = new URLSearchParams({ username, password });
  return request<{ access_token: string; token_type: string }>("/auth/login", undefined, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
}

export const api = {
  login,
  me: (token: string) => request<Usuario>("/auth/me", token),
  resumo: (token: string) => request<Resumo>("/dashboard/resumo", token),
  produtos: (token: string, busca = "") =>
    request<Produto[]>(`/produtos${busca ? `?busca=${encodeURIComponent(busca)}` : ""}`, token),
  estoqueBaixo: (token: string) => request<Produto[]>("/produtos/estoque-baixo?limite=5", token),
  criarProduto: (token: string, produto: Omit<Produto, "id">) =>
    request<Produto>("/produtos", token, { method: "POST", body: JSON.stringify(produto) }),
  atualizarProduto: (token: string, id: number, produto: Partial<Omit<Produto, "id">>) =>
    request<Produto>(`/produtos/${id}`, token, { method: "PUT", body: JSON.stringify(produto) }),
  excluirProduto: (token: string, id: number) =>
    request<void>(`/produtos/${id}`, token, { method: "DELETE" }),
  vendas: (token: string) => request<Venda[]>("/vendas", token),
  registrarVenda: (token: string, itens: { produto_id: number; quantidade: number }[]) =>
    request<Venda>("/vendas", token, { method: "POST", body: JSON.stringify({ itens }) }),
};
