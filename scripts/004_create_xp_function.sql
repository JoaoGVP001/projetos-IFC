-- Function to increment user XP and level up
create or replace function increment_user_xp(user_id uuid, xp_amount integer)
returns void
language plpgsql
security definer
as $$
declare
  current_xp integer;
  current_level integer;
  new_xp integer;
  new_level integer;
begin
  -- Get current XP and level
  select xp, level into current_xp, current_level
  from profiles
  where id = user_id;

  -- Calculate new XP
  new_xp := current_xp + xp_amount;
  
  -- Calculate new level (every 100 XP = 1 level)
  new_level := floor(new_xp / 100) + 1;

  -- Update profile
  update profiles
  set 
    xp = new_xp,
    level = new_level,
    total_questions_answered = total_questions_answered + 1,
    updated_at = now()
  where id = user_id;
end;
$$;
