-- Add new learning paths for the 7 new subjects
insert into public.learning_paths (subject, title, description, icon, order_index) values
  ('physics', 'Física', 'Mecânica, Termodinâmica, Eletromagnetismo e mais', '⚛️', 4),
  ('chemistry', 'Química', 'Química Geral, Orgânica e Inorgânica', '🧪', 5),
  ('history', 'História', 'História do Brasil e História Geral', '📜', 6),
  ('geography', 'Geografia', 'Geografia Física e Humana', '🌍', 7),
  ('philosophy', 'Filosofia', 'Filosofia Antiga, Moderna e Contemporânea', '🤔', 8),
  ('sociology', 'Sociologia', 'Sociedade, Cultura e Política', '👥', 9),
  ('english', 'Inglês', 'Gramática, Vocabulário e Interpretação', '🇬🇧', 10);

-- Add sample topics for Physics
insert into public.topics (learning_path_id, title, description, order_index, xp_reward)
select 
  lp.id,
  t.title,
  t.description,
  t.order_index,
  t.xp_reward
from public.learning_paths lp
cross join (values
  ('Cinemática', 'Movimento, velocidade e aceleração', 1, 15),
  ('Dinâmica', 'Leis de Newton e forças', 2, 20),
  ('Energia e Trabalho', 'Energia cinética, potencial e conservação', 3, 20),
  ('Termodinâmica', 'Calor, temperatura e leis da termodinâmica', 4, 25),
  ('Eletrostática', 'Cargas elétricas e campo elétrico', 5, 25),
  ('Eletrodinâmica', 'Corrente elétrica e circuitos', 6, 30)
) as t(title, description, order_index, xp_reward)
where lp.subject = 'physics';

-- Add sample topics for Chemistry
insert into public.topics (learning_path_id, title, description, order_index, xp_reward)
select 
  lp.id,
  t.title,
  t.description,
  t.order_index,
  t.xp_reward
from public.learning_paths lp
cross join (values
  ('Estrutura Atômica', 'Átomos, íons e tabela periódica', 1, 15),
  ('Ligações Químicas', 'Ligações iônicas, covalentes e metálicas', 2, 20),
  ('Reações Químicas', 'Tipos de reações e balanceamento', 3, 20),
  ('Estequiometria', 'Cálculos químicos e mol', 4, 25),
  ('Química Orgânica', 'Hidrocarbonetos e funções orgânicas', 5, 25),
  ('Termoquímica', 'Entalpia e energia nas reações', 6, 30)
) as t(title, description, order_index, xp_reward)
where lp.subject = 'chemistry';

-- Add sample topics for History
insert into public.topics (learning_path_id, title, description, order_index, xp_reward)
select 
  lp.id,
  t.title,
  t.description,
  t.order_index,
  t.xp_reward
from public.learning_paths lp
cross join (values
  ('Brasil Colônia', 'Descobrimento e colonização portuguesa', 1, 15),
  ('Brasil Império', 'Independência e período imperial', 2, 20),
  ('República Velha', 'Proclamação da República até 1930', 3, 20),
  ('Era Vargas', 'Governo Vargas e Estado Novo', 4, 25),
  ('Ditadura Militar', 'Regime militar no Brasil', 5, 25),
  ('Redemocratização', 'Nova República e Constituição de 1988', 6, 30)
) as t(title, description, order_index, xp_reward)
where lp.subject = 'history';

-- Add sample topics for Geography
insert into public.topics (learning_path_id, title, description, order_index, xp_reward)
select 
  lp.id,
  t.title,
  t.description,
  t.order_index,
  t.xp_reward
from public.learning_paths lp
cross join (values
  ('Cartografia', 'Mapas, escalas e projeções', 1, 15),
  ('Geologia', 'Estrutura da Terra e rochas', 2, 20),
  ('Clima', 'Fatores climáticos e tipos de clima', 3, 20),
  ('Hidrografia', 'Bacias hidrográficas e recursos hídricos', 4, 25),
  ('População', 'Demografia e movimentos populacionais', 5, 25),
  ('Urbanização', 'Cidades e problemas urbanos', 6, 30)
) as t(title, description, order_index, xp_reward)
where lp.subject = 'geography';

-- Add sample topics for Philosophy
insert into public.topics (learning_path_id, title, description, order_index, xp_reward)
select 
  lp.id,
  t.title,
  t.description,
  t.order_index,
  t.xp_reward
from public.learning_paths lp
cross join (values
  ('Filosofia Antiga', 'Sócrates, Platão e Aristóteles', 1, 15),
  ('Filosofia Medieval', 'Santo Agostinho e São Tomás de Aquino', 2, 20),
  ('Filosofia Moderna', 'Descartes, Kant e Iluminismo', 3, 20),
  ('Filosofia Contemporânea', 'Nietzsche, Sartre e existencialismo', 4, 25),
  ('Ética', 'Moral, valores e dilemas éticos', 5, 25),
  ('Política', 'Estado, poder e democracia', 6, 30)
) as t(title, description, order_index, xp_reward)
where lp.subject = 'philosophy';

-- Add sample topics for Sociology
insert into public.topics (learning_path_id, title, description, order_index, xp_reward)
select 
  lp.id,
  t.title,
  t.description,
  t.order_index,
  t.xp_reward
from public.learning_paths lp
cross join (values
  ('Introdução à Sociologia', 'Conceitos básicos e fundadores', 1, 15),
  ('Cultura', 'Cultura, identidade e diversidade', 2, 20),
  ('Estratificação Social', 'Classes sociais e desigualdade', 3, 20),
  ('Instituições Sociais', 'Família, escola e religião', 4, 25),
  ('Movimentos Sociais', 'Ação coletiva e mudança social', 5, 25),
  ('Globalização', 'Mundo globalizado e suas consequências', 6, 30)
) as t(title, description, order_index, xp_reward)
where lp.subject = 'sociology';

-- Add sample topics for English
insert into public.topics (learning_path_id, title, description, order_index, xp_reward)
select 
  lp.id,
  t.title,
  t.description,
  t.order_index,
  t.xp_reward
from public.learning_paths lp
cross join (values
  ('Verb Tenses', 'Present, past and future tenses', 1, 15),
  ('Modal Verbs', 'Can, could, should, must, etc.', 2, 20),
  ('Conditionals', 'If clauses and conditional sentences', 3, 20),
  ('Passive Voice', 'Active and passive constructions', 4, 25),
  ('Reading Comprehension', 'Text interpretation strategies', 5, 25),
  ('Vocabulary', 'Common words and expressions', 6, 30)
) as t(title, description, order_index, xp_reward)
where lp.subject = 'english';
