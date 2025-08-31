-- Inserir empresa de exemplo
INSERT INTO companies (id, name, document, email, phone, address, city, state, zip_code)
VALUES (
  'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
  'TrustV Sistemas',
  '12.345.678/0001-90',
  'contato@trustv.com.br',
  '(11) 99999-9999',
  'Rua das Empresas, 123',
  'São Paulo',
  'SP',
  '01234-567'
) ON CONFLICT (document) DO NOTHING;

-- Inserir categorias de exemplo
INSERT INTO product_categories (company_id, name, description)
VALUES 
  ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Eletrônicos', 'Produtos eletrônicos em geral'),
  ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Informática', 'Equipamentos de informática'),
  ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Escritório', 'Material de escritório')
ON CONFLICT (company_id, name) DO NOTHING;
