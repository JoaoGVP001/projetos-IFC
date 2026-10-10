-- Tabela de produtos
CREATE TABLE IF NOT EXISTS products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  category_id UUID REFERENCES product_categories(id),
  sku VARCHAR(100) NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  unit_of_measure VARCHAR(20) NOT NULL DEFAULT 'UN',
  cost_price DECIMAL(15,2) DEFAULT 0,
  sale_price DECIMAL(15,2) DEFAULT 0,
  min_stock DECIMAL(15,3) DEFAULT 0,
  max_stock DECIMAL(15,3),
  current_stock DECIMAL(15,3) DEFAULT 0,
  
  -- Campos fiscais
  ncm VARCHAR(10),
  cfop VARCHAR(4),
  icms_rate DECIMAL(5,2) DEFAULT 0,
  ipi_rate DECIMAL(5,2) DEFAULT 0,
  pis_rate DECIMAL(5,2) DEFAULT 0,
  cofins_rate DECIMAL(5,2) DEFAULT 0,
  
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_by UUID REFERENCES auth.users(id),
  updated_by UUID REFERENCES auth.users(id),
  
  UNIQUE(company_id, sku)
);

-- Enable RLS
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- Policies for products
CREATE POLICY "Users can view products from their companies" ON products
  FOR SELECT USING (
    company_id IN (
      SELECT company_id FROM user_companies 
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Admins and sellers can manage products" ON products
  FOR ALL USING (
    company_id IN (
      SELECT company_id FROM user_companies 
      WHERE user_id = auth.uid() AND role IN ('admin', 'seller')
    )
  );
