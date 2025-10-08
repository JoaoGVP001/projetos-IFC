-- Seed Learning Paths
insert into public.learning_paths (subject, title, description, icon, order_index) values
  ('math', 'Matemática ENEM', 'Prepare-se para o ENEM com questões de matemática', '📐', 1),
  ('portuguese', 'Português ENEM', 'Domine a língua portuguesa para o ENEM', '📚', 2),
  ('biology', 'Biologia ENEM', 'Estude biologia de forma gamificada', '🧬', 3);

-- Seed Math Topics
insert into public.topics (learning_path_id, title, description, order_index, xp_reward)
select 
  lp.id,
  t.title,
  t.description,
  t.order_index,
  t.xp_reward
from public.learning_paths lp
cross join (
  values
    ('Números e Operações', 'Operações básicas, frações, porcentagem', 1, 10),
    ('Álgebra', 'Equações, inequações e funções', 2, 15),
    ('Geometria Plana', 'Áreas, perímetros e teoremas', 3, 15),
    ('Geometria Espacial', 'Volumes e áreas de sólidos', 4, 20),
    ('Trigonometria', 'Seno, cosseno e aplicações', 5, 20),
    ('Estatística', 'Média, mediana, moda e gráficos', 6, 15),
    ('Probabilidade', 'Cálculo de probabilidades', 7, 15),
    ('Matemática Financeira', 'Juros simples e compostos', 8, 15)
) as t(title, description, order_index, xp_reward)
where lp.subject = 'math';

-- Seed Portuguese Topics
insert into public.topics (learning_path_id, title, description, order_index, xp_reward)
select 
  lp.id,
  t.title,
  t.description,
  t.order_index,
  t.xp_reward
from public.learning_paths lp
cross join (
  values
    ('Interpretação de Texto', 'Compreensão e análise textual', 1, 10),
    ('Gramática', 'Classes gramaticais e sintaxe', 2, 15),
    ('Literatura Brasileira', 'Escolas literárias e autores', 3, 15),
    ('Redação', 'Estrutura e argumentação', 4, 20),
    ('Figuras de Linguagem', 'Metáfora, metonímia e outras', 5, 15),
    ('Ortografia', 'Regras de escrita correta', 6, 10),
    ('Pontuação', 'Uso correto de vírgulas e pontos', 7, 10),
    ('Coesão e Coerência', 'Conectivos e estrutura textual', 8, 15)
) as t(title, description, order_index, xp_reward)
where lp.subject = 'portuguese';

-- Seed Biology Topics
insert into public.topics (learning_path_id, title, description, order_index, xp_reward)
select 
  lp.id,
  t.title,
  t.description,
  t.order_index,
  t.xp_reward
from public.learning_paths lp
cross join (
  values
    ('Citologia', 'Estrutura e função celular', 1, 10),
    ('Genética', 'Hereditariedade e DNA', 2, 15),
    ('Evolução', 'Teorias evolutivas', 3, 15),
    ('Ecologia', 'Relações ecológicas e biomas', 4, 15),
    ('Fisiologia Humana', 'Sistemas do corpo humano', 5, 20),
    ('Botânica', 'Reino vegetal', 6, 15),
    ('Zoologia', 'Reino animal', 7, 15),
    ('Microbiologia', 'Vírus, bactérias e fungos', 8, 15)
) as t(title, description, order_index, xp_reward)
where lp.subject = 'biology';

-- Seed Achievements
insert into public.achievements (title, description, icon, requirement_type, requirement_value, xp_reward) values
  ('Primeiro Passo', 'Complete sua primeira questão', '🎯', 'questions_answered', 1, 50),
  ('Estudante Dedicado', 'Responda 10 questões', '📖', 'questions_answered', 10, 100),
  ('Mestre do Conhecimento', 'Responda 100 questões', '🎓', 'questions_answered', 100, 500),
  ('Sequência de Fogo', 'Mantenha uma sequência de 7 dias', '🔥', 'streak', 7, 200),
  ('Maratonista', 'Mantenha uma sequência de 30 dias', '🏃', 'streak', 30, 1000),
  ('Perfeccionista', 'Acerte 50 questões seguidas', '💯', 'correct_streak', 50, 300),
  ('Nível 10', 'Alcance o nível 10', '⭐', 'level', 10, 500),
  ('Campeão', 'Vença um campeonato', '🏆', 'championships_won', 1, 500);
