-- Função para atualizar estoque automaticamente
CREATE OR REPLACE FUNCTION update_product_stock()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    -- Atualizar estoque baseado no tipo de movimentação
    IF NEW.type = 'entry' OR NEW.type = 'return' THEN
      UPDATE products 
      SET current_stock = current_stock + NEW.quantity,
          updated_at = NOW()
      WHERE id = NEW.product_id;
    ELSIF NEW.type = 'exit' THEN
      UPDATE products 
      SET current_stock = current_stock - NEW.quantity,
          updated_at = NOW()
      WHERE id = NEW.product_id;
    ELSIF NEW.type = 'adjustment' THEN
      UPDATE products 
      SET current_stock = NEW.quantity,
          updated_at = NOW()
      WHERE id = NEW.product_id;
    END IF;
  END IF;
  
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Criar trigger para atualizar estoque
DROP TRIGGER IF EXISTS trigger_update_product_stock ON inventory_movements;
CREATE TRIGGER trigger_update_product_stock
  AFTER INSERT ON inventory_movements
  FOR EACH ROW
  EXECUTE FUNCTION update_product_stock();

-- Função para criar perfil de usuário automaticamente
CREATE OR REPLACE FUNCTION create_user_profile()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO user_profiles (id, email, full_name)
  VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Criar trigger para criar perfil automaticamente
DROP TRIGGER IF EXISTS trigger_create_user_profile ON auth.users;
CREATE TRIGGER trigger_create_user_profile
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION create_user_profile();
