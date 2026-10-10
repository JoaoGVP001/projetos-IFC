export type KnowledgeSystem = "Small Commerce" | "ZWeb" | "Interno";

export type KnowledgeTone = "small" | "zweb" | "internal";

export type KnowledgeItem = {
  id: string;
  system: KnowledgeSystem;
  tone: KnowledgeTone;
  title: string;
  category: string;
  module: string;
  tags: string[];
  views: number;
  excerpt: string;
  procedure: string;
  sourceLabel: string;
  sourceUrl?: string;
};

export const initialKnowledge: KnowledgeItem[] = [
  {
    id: "small-reforma-tributaria",
    system: "Small Commerce",
    tone: "small",
    title: "Reforma tributária: primeiros passos",
    category: "Fiscal · Configurações",
    module: "Estoque e documentos fiscais",
    tags: ["CBS", "IBS", "NF-e", "NFC-e", "tributação"],
    views: 128,
    excerpt: "Orientações iniciais para revisar a tributação dos produtos e preparar a emissão dos documentos fiscais.",
    procedure: "Confirme o regime tributário com a contabilidade, mantenha o sistema atualizado e revise os campos CBS/IBS no cadastro do produto antes de emitir o documento fiscal.",
    sourceLabel: "BDC Small Commerce",
    sourceUrl: "https://bdc.smallsoft.com.br/artigos/reforma-tributaria-primeiros-passos/",
  },
  {
    id: "zweb-sicoob-api",
    system: "ZWeb",
    tone: "zweb",
    title: "Ativação da API para boletos Sicoob",
    category: "Financeiro · Integrações",
    module: "Boletos",
    tags: ["Sicoob", "API", "boleto", "financeiro"],
    views: 94,
    excerpt: "Checklist demonstrativo para conferir a integração de boletos antes de orientar o cliente.",
    procedure: "Valide os dados bancários cadastrados, confira se a integração está habilitada para a empresa e teste a emissão em um ambiente autorizado antes de liberar o uso.",
    sourceLabel: "BDC ZWeb",
    sourceUrl: "https://bdc.zweb.com.br/",
  },
  {
    id: "interno-certificado",
    system: "Interno",
    tone: "internal",
    title: "Certificado não comunica: diagnóstico seguro",
    category: "Procedimentos · Certificado",
    module: "Certificado digital",
    tags: ["certificado", "A1", "A3", "comunicação"],
    views: 76,
    excerpt: "Sequência segura de diagnóstico sem copiar senhas, certificados ou dados do cliente para o atendimento.",
    procedure: "Confirme validade e tipo do certificado, teste a comunicação no próprio ambiente do cliente e registre somente o resultado técnico. Nunca copie o arquivo do certificado ou sua senha para a central.",
    sourceLabel: "Conteúdo interno demonstrativo",
  },
  {
    id: "small-status-servico",
    system: "Small Commerce",
    tone: "small",
    title: "Erro ao consultar o status de serviço",
    category: "Fiscal · Comunicação",
    module: "NF-e e NFC-e",
    tags: ["SEFAZ", "status", "serviço", "conexão"],
    views: 61,
    excerpt: "Roteiro inicial para separar indisponibilidade externa de problema local de comunicação.",
    procedure: "Verifique a conexão do computador, confirme o ambiente de emissão e consulte a disponibilidade do serviço autorizado. Se a fonte não trouxer evidência suficiente, encaminhe para análise técnica.",
    sourceLabel: "BDC Small Commerce",
    sourceUrl: "https://bdc.smallsoft.com.br/artigos/erro-ao-consultar-o-status-de-servico/",
  },
  {
    id: "zweb-rejeicao-ie",
    system: "ZWeb",
    tone: "zweb",
    title: "Rejeição: IE do emitente não vinculada ao CNPJ",
    category: "Fiscal · Rejeições",
    module: "NF-e",
    tags: ["rejeição", "IE", "CNPJ", "emitente"],
    views: 52,
    excerpt: "Validação cadastral inicial para rejeições envolvendo inscrição estadual e CNPJ do emitente.",
    procedure: "Compare os dados do emitente no cadastro com a situação cadastral oficial. Não altere informações fiscais sem a confirmação do cliente e de sua contabilidade.",
    sourceLabel: "BDC ZWeb",
    sourceUrl: "https://bdc.zweb.com.br/",
  },
  {
    id: "interno-backup",
    system: "Interno",
    tone: "internal",
    title: "Backup: conferência antes de orientar a restauração",
    category: "Procedimentos · Segurança",
    module: "Banco de dados",
    tags: ["backup", "restauração", "segurança", "banco"],
    views: 47,
    excerpt: "Checklist de segurança para evitar sobrescrever a base errada durante uma restauração.",
    procedure: "Confirme empresa, data, tamanho e integridade do arquivo. Preserve a base atual em uma cópia separada e faça a restauração somente em ambiente autorizado e com janela de manutenção.",
    sourceLabel: "Conteúdo interno demonstrativo",
  },
];

