-- Tabela de relacionamento usuário-empresa
CREATE TABLE IF NOT EXISTS user_companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'seller', 'accountant')),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, company_id)
);

-- Enable RLS
ALTER TABLE user_companies ENABLE ROW LEVEL SECURITY;

-- Policies for user_companies
CREATE POLICY "Users can view their own company relationships" ON user_companies
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Company admins can manage company users" ON user_companies
  FOR ALL USING (
    company_id IN (
      SELECT company_id FROM user_companies 
      WHERE user_id = auth.uid() AND role = 'admin'
    )
  );

CREATE POLICY "Site admins can manage all relationships" ON user_companies
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM user_profiles 
      WHERE user_id = auth.uid() AND role = 'site_admin'
    )
  );
