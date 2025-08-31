-- Tabela de movimentações de estoque
CREATE TABLE IF NOT EXISTS inventory_movements (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  movement_type VARCHAR(20) NOT NULL CHECK (movement_type IN ('entry', 'exit', 'return', 'adjustment')),
  quantity DECIMAL(15,3) NOT NULL,
  unit_cost DECIMAL(15,2),
  total_cost DECIMAL(15,2),
  
  -- Referências para documentos
  document_number VARCHAR(100),
  document_type VARCHAR(50),
  supplier_customer VARCHAR(255),
  
  -- Campos fiscais
  invoice_number VARCHAR(100),
  invoice_date DATE,
  cfop VARCHAR(4),
  icms_value DECIMAL(15,2) DEFAULT 0,
  ipi_value DECIMAL(15,2) DEFAULT 0,
  pis_value DECIMAL(15,2) DEFAULT 0,
  cofins_value DECIMAL(15,2) DEFAULT 0,
  
  notes TEXT,
  movement_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_by UUID NOT NULL REFERENCES auth.users(id)
);

-- Enable RLS
ALTER TABLE inventory_movements ENABLE ROW LEVEL SECURITY;

-- Policies for inventory_movements
CREATE POLICY "Users can view movements from their companies" ON inventory_movements
  FOR SELECT USING (
    company_id IN (
      SELECT company_id FROM user_companies 
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Admins and sellers can create movements" ON inventory_movements
  FOR INSERT WITH CHECK (
    company_id IN (
      SELECT company_id FROM user_companies 
      WHERE user_id = auth.uid() AND role IN ('admin', 'seller')
    ) AND created_by = auth.uid()
  );

CREATE POLICY "Only admins can update/delete movements" ON inventory_movements
  FOR UPDATE USING (
    company_id IN (
      SELECT company_id FROM user_companies 
      WHERE user_id = auth.uid() AND role = 'admin'
    )
  );
