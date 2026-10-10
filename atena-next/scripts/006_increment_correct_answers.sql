-- Function to increment correct answers
create or replace function increment_correct_answers(user_id uuid)
returns void
language plpgsql
security definer
as $$
begin
  update profiles
  set correct_answers = correct_answers + 1
  where id = user_id;
end;
$$;
