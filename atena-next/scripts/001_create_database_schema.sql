-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Create enum types
create type user_role as enum ('student', 'teacher');
create type subject_type as enum ('math', 'portuguese', 'biology');
create type question_difficulty as enum ('easy', 'medium', 'hard');
create type championship_status as enum ('upcoming', 'active', 'completed');

-- Users/Profiles table (extends auth.users)
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text not null,
  full_name text not null,
  role user_role not null default 'student',
  avatar_url text,
  xp integer not null default 0,
  level integer not null default 1,
  current_streak integer not null default 0,
  longest_streak integer not null default 0,
  last_activity_date date,
  total_questions_answered integer not null default 0,
  correct_answers integer not null default 0,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

-- Learning paths table
create table if not exists public.learning_paths (
  id uuid primary key default uuid_generate_v4(),
  subject subject_type not null,
  title text not null,
  description text,
  icon text,
  order_index integer not null,
  created_at timestamp with time zone default now()
);

-- Topics within learning paths
create table if not exists public.topics (
  id uuid primary key default uuid_generate_v4(),
  learning_path_id uuid references public.learning_paths(id) on delete cascade,
  title text not null,
  description text,
  order_index integer not null,
  xp_reward integer not null default 10,
  created_at timestamp with time zone default now()
);

-- Questions bank
create table if not exists public.questions (
  id uuid primary key default uuid_generate_v4(),
  topic_id uuid references public.topics(id) on delete cascade,
  question_text text not null,
  question_type text not null default 'multiple_choice',
  difficulty question_difficulty not null default 'medium',
  xp_value integer not null default 10,
  explanation text,
  created_by uuid references public.profiles(id),
  created_at timestamp with time zone default now()
);

-- Question options (for multiple choice)
create table if not exists public.question_options (
  id uuid primary key default uuid_generate_v4(),
  question_id uuid references public.questions(id) on delete cascade,
  option_text text not null,
  is_correct boolean not null default false,
  order_index integer not null
);

-- User progress on topics
create table if not exists public.user_topic_progress (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid references public.profiles(id) on delete cascade,
  topic_id uuid references public.topics(id) on delete cascade,
  is_completed boolean not null default false,
  questions_answered integer not null default 0,
  correct_answers integer not null default 0,
  xp_earned integer not null default 0,
  last_practiced_at timestamp with time zone,
  completed_at timestamp with time zone,
  unique(user_id, topic_id)
);

-- User answers history
create table if not exists public.user_answers (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid references public.profiles(id) on delete cascade,
  question_id uuid references public.questions(id) on delete cascade,
  selected_option_id uuid references public.question_options(id),
  is_correct boolean not null,
  xp_earned integer not null default 0,
  answered_at timestamp with time zone default now()
);

-- Achievements/Badges
create table if not exists public.achievements (
  id uuid primary key default uuid_generate_v4(),
  title text not null,
  description text not null,
  icon text not null,
  requirement_type text not null,
  requirement_value integer not null,
  xp_reward integer not null default 50,
  created_at timestamp with time zone default now()
);

-- User achievements
create table if not exists public.user_achievements (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid references public.profiles(id) on delete cascade,
  achievement_id uuid references public.achievements(id) on delete cascade,
  earned_at timestamp with time zone default now(),
  unique(user_id, achievement_id)
);

-- Championships
create table if not exists public.championships (
  id uuid primary key default uuid_generate_v4(),
  title text not null,
  description text,
  created_by uuid references public.profiles(id),
  subject subject_type not null,
  start_date timestamp with time zone not null,
  end_date timestamp with time zone not null,
  status championship_status not null default 'upcoming',
  max_participants integer,
  created_at timestamp with time zone default now()
);

-- Championship participants
create table if not exists public.championship_participants (
  id uuid primary key default uuid_generate_v4(),
  championship_id uuid references public.championships(id) on delete cascade,
  user_id uuid references public.profiles(id) on delete cascade,
  score integer not null default 0,
  rank integer,
  joined_at timestamp with time zone default now(),
  unique(championship_id, user_id)
);

-- Championship questions
create table if not exists public.championship_questions (
  id uuid primary key default uuid_generate_v4(),
  championship_id uuid references public.championships(id) on delete cascade,
  question_id uuid references public.questions(id) on delete cascade,
  order_index integer not null
);

-- Friends system
create table if not exists public.friendships (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid references public.profiles(id) on delete cascade,
  friend_id uuid references public.profiles(id) on delete cascade,
  status text not null default 'pending',
  created_at timestamp with time zone default now(),
  unique(user_id, friend_id)
);

-- Notifications
create table if not exists public.notifications (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid references public.profiles(id) on delete cascade,
  title text not null,
  message text not null,
  type text not null,
  is_read boolean not null default false,
  created_at timestamp with time zone default now()
);

-- Daily activity tracking for streaks
create table if not exists public.daily_activities (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid references public.profiles(id) on delete cascade,
  activity_date date not null,
  questions_answered integer not null default 0,
  xp_earned integer not null default 0,
  unique(user_id, activity_date)
);

-- Enable Row Level Security on all tables
alter table public.profiles enable row level security;
alter table public.learning_paths enable row level security;
alter table public.topics enable row level security;
alter table public.questions enable row level security;
alter table public.question_options enable row level security;
alter table public.user_topic_progress enable row level security;
alter table public.user_answers enable row level security;
alter table public.achievements enable row level security;
alter table public.user_achievements enable row level security;
alter table public.championships enable row level security;
alter table public.championship_participants enable row level security;
alter table public.championship_questions enable row level security;
alter table public.friendships enable row level security;
alter table public.notifications enable row level security;
alter table public.daily_activities enable row level security;

-- RLS Policies for profiles
create policy "Users can view all profiles"
  on public.profiles for select
  using (true);

create policy "Users can update own profile"
  on public.profiles for update
  using (auth.uid() = id);

create policy "Users can insert own profile"
  on public.profiles for insert
  with check (auth.uid() = id);

-- RLS Policies for learning_paths (public read)
create policy "Anyone can view learning paths"
  on public.learning_paths for select
  using (true);

create policy "Teachers can create learning paths"
  on public.learning_paths for insert
  with check (
    exists (
      select 1 from public.profiles
      where id = auth.uid() and role = 'teacher'
    )
  );

-- RLS Policies for topics (public read)
create policy "Anyone can view topics"
  on public.topics for select
  using (true);

create policy "Teachers can create topics"
  on public.topics for insert
  with check (
    exists (
      select 1 from public.profiles
      where id = auth.uid() and role = 'teacher'
    )
  );

-- RLS Policies for questions (public read)
create policy "Anyone can view questions"
  on public.questions for select
  using (true);

create policy "Teachers can create questions"
  on public.questions for insert
  with check (
    exists (
      select 1 from public.profiles
      where id = auth.uid() and role = 'teacher'
    )
  );

-- RLS Policies for question_options (public read)
create policy "Anyone can view question options"
  on public.question_options for select
  using (true);

-- RLS Policies for user_topic_progress
create policy "Users can view own progress"
  on public.user_topic_progress for select
  using (auth.uid() = user_id);

create policy "Users can insert own progress"
  on public.user_topic_progress for insert
  with check (auth.uid() = user_id);

create policy "Users can update own progress"
  on public.user_topic_progress for update
  using (auth.uid() = user_id);

-- RLS Policies for user_answers
create policy "Users can view own answers"
  on public.user_answers for select
  using (auth.uid() = user_id);

create policy "Users can insert own answers"
  on public.user_answers for insert
  with check (auth.uid() = user_id);

-- RLS Policies for achievements (public read)
create policy "Anyone can view achievements"
  on public.achievements for select
  using (true);

-- RLS Policies for user_achievements
create policy "Users can view own achievements"
  on public.user_achievements for select
  using (auth.uid() = user_id);

create policy "Users can insert own achievements"
  on public.user_achievements for insert
  with check (auth.uid() = user_id);

-- RLS Policies for championships (public read)
create policy "Anyone can view championships"
  on public.championships for select
  using (true);

create policy "Teachers can create championships"
  on public.championships for insert
  with check (
    exists (
      select 1 from public.profiles
      where id = auth.uid() and role = 'teacher'
    )
  );

-- RLS Policies for championship_participants
create policy "Anyone can view championship participants"
  on public.championship_participants for select
  using (true);

create policy "Users can join championships"
  on public.championship_participants for insert
  with check (auth.uid() = user_id);

-- RLS Policies for championship_questions (public read)
create policy "Anyone can view championship questions"
  on public.championship_questions for select
  using (true);

-- RLS Policies for friendships
create policy "Users can view own friendships"
  on public.friendships for select
  using (auth.uid() = user_id or auth.uid() = friend_id);

create policy "Users can create friendships"
  on public.friendships for insert
  with check (auth.uid() = user_id);

create policy "Users can update own friendships"
  on public.friendships for update
  using (auth.uid() = user_id or auth.uid() = friend_id);

-- RLS Policies for notifications
create policy "Users can view own notifications"
  on public.notifications for select
  using (auth.uid() = user_id);

create policy "Users can update own notifications"
  on public.notifications for update
  using (auth.uid() = user_id);

-- RLS Policies for daily_activities
create policy "Users can view own daily activities"
  on public.daily_activities for select
  using (auth.uid() = user_id);

create policy "Users can insert own daily activities"
  on public.daily_activities for insert
  with check (auth.uid() = user_id);

create policy "Users can update own daily activities"
  on public.daily_activities for update
  using (auth.uid() = user_id);

-- Create indexes for better performance
create index idx_profiles_role on public.profiles(role);
create index idx_profiles_xp on public.profiles(xp desc);
create index idx_topics_learning_path on public.topics(learning_path_id);
create index idx_questions_topic on public.questions(topic_id);
create index idx_user_topic_progress_user on public.user_topic_progress(user_id);
create index idx_user_answers_user on public.user_answers(user_id);
create index idx_championships_status on public.championships(status);
create index idx_championship_participants_championship on public.championship_participants(championship_id);
create index idx_daily_activities_user_date on public.daily_activities(user_id, activity_date);
