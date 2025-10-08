-- Function to check and award achievements
create or replace function check_and_award_achievements(p_user_id uuid)
returns void
language plpgsql
security definer
as $$
declare
  v_profile record;
  v_achievement record;
  v_already_earned boolean;
begin
  -- Get user profile
  select * into v_profile
  from profiles
  where id = p_user_id;

  -- Loop through all achievements
  for v_achievement in select * from achievements loop
    -- Check if user already has this achievement
    select exists(
      select 1 from user_achievements
      where user_id = p_user_id and achievement_id = v_achievement.id
    ) into v_already_earned;

    -- Skip if already earned
    if v_already_earned then
      continue;
    end if;

    -- Check if user meets the requirement
    case v_achievement.requirement_type
      when 'questions_answered' then
        if v_profile.total_questions_answered >= v_achievement.requirement_value then
          -- Award achievement
          insert into user_achievements (user_id, achievement_id)
          values (p_user_id, v_achievement.id);
          
          -- Award XP
          update profiles
          set xp = xp + v_achievement.xp_reward
          where id = p_user_id;
        end if;

      when 'streak' then
        if v_profile.current_streak >= v_achievement.requirement_value then
          insert into user_achievements (user_id, achievement_id)
          values (p_user_id, v_achievement.id);
          
          update profiles
          set xp = xp + v_achievement.xp_reward
          where id = p_user_id;
        end if;

      when 'level' then
        if v_profile.level >= v_achievement.requirement_value then
          insert into user_achievements (user_id, achievement_id)
          values (p_user_id, v_achievement.id);
          
          update profiles
          set xp = xp + v_achievement.xp_reward
          where id = p_user_id;
        end if;
    end case;
  end loop;
end;
$$;

-- Function to update streak
create or replace function update_user_streak(p_user_id uuid)
returns void
language plpgsql
security definer
as $$
declare
  v_last_activity date;
  v_today date;
  v_current_streak integer;
  v_longest_streak integer;
begin
  v_today := current_date;
  
  -- Get user's last activity and streaks
  select last_activity_date, current_streak, longest_streak
  into v_last_activity, v_current_streak, v_longest_streak
  from profiles
  where id = p_user_id;

  -- If no previous activity or activity is today, just update last_activity_date
  if v_last_activity is null or v_last_activity = v_today then
    update profiles
    set last_activity_date = v_today
    where id = p_user_id;
    return;
  end if;

  -- If last activity was yesterday, increment streak
  if v_last_activity = v_today - interval '1 day' then
    v_current_streak := v_current_streak + 1;
    
    -- Update longest streak if needed
    if v_current_streak > v_longest_streak then
      v_longest_streak := v_current_streak;
    end if;
    
    update profiles
    set 
      current_streak = v_current_streak,
      longest_streak = v_longest_streak,
      last_activity_date = v_today
    where id = p_user_id;
  else
    -- Streak broken, reset to 1
    update profiles
    set 
      current_streak = 1,
      last_activity_date = v_today
    where id = p_user_id;
  end if;

  -- Check for streak achievements
  perform check_and_award_achievements(p_user_id);
end;
$$;
