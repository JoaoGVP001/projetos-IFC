-- Dados iniciais para teste
INSERT INTO companies (id, name, cnpj, email, city, state) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'Empresa Demo LTDA', '12.345.678/0001-90', 'contato@empresademo.com', 'São Paulo', 'SP');

-- Categorias de exemplo
INSERT INTO product_categories (company_id, name, description) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'Eletrônicos', 'Produtos eletrônicos diversos'),
('550e8400-e29b-41d4-a716-446655440000', 'Roupas', 'Vestuário em geral'),
('550e8400-e29b-41d4-a716-446655440000', 'Casa e Jardim', 'Produtos para casa e jardim');
