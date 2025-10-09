-- Add new subjects to the enum
-- First, we need to drop and recreate the enum with all subjects
-- This is done by creating a new enum and migrating the data

-- Create new enum with all subjects
create type subject_type_new as enum (
  'math', 
  'portuguese', 
  'biology',
  'physics',
  'chemistry',
  'history',
  'geography',
  'philosophy',
  'sociology',
  'english'
);

-- Update tables to use new enum
alter table public.learning_paths 
  alter column subject type subject_type_new 
  using subject::text::subject_type_new;

alter table public.championships 
  alter column subject type subject_type_new 
  using subject::text::subject_type_new;

-- Drop old enum and rename new one
drop type subject_type;
alter type subject_type_new rename to subject_type;

-- Create classes (turmas) table
create table if not exists public.classes (
  id uuid primary key default uuid_generate_v4(),
  name text not null,
  description text,
  teacher_id uuid references public.profiles(id) on delete cascade,
  access_code text not null unique,
  max_students integer,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

-- Create class_students table (many-to-many relationship)
create table if not exists public.class_students (
  id uuid primary key default uuid_generate_v4(),
  class_id uuid references public.classes(id) on delete cascade,
  student_id uuid references public.profiles(id) on delete cascade,
  joined_at timestamp with time zone default now(),
  unique(class_id, student_id)
);

-- Enable RLS on new tables
alter table public.classes enable row level security;
alter table public.class_students enable row level security;

-- RLS Policies for classes
create policy "Anyone can view classes"
  on public.classes for select
  using (true);

create policy "Teachers can create classes"
  on public.classes for insert
  with check (
    exists (
      select 1 from public.profiles
      where id = auth.uid() and role = 'teacher'
    )
  );

create policy "Teachers can update own classes"
  on public.classes for update
  using (auth.uid() = teacher_id);

create policy "Teachers can delete own classes"
  on public.classes for delete
  using (auth.uid() = teacher_id);

-- RLS Policies for class_students
create policy "Anyone can view class students"
  on public.class_students for select
  using (true);

create policy "Students can join classes"
  on public.class_students for insert
  with check (auth.uid() = student_id);

create policy "Students can leave classes"
  on public.class_students for delete
  using (auth.uid() = student_id);

create policy "Teachers can remove students from their classes"
  on public.class_students for delete
  using (
    exists (
      select 1 from public.classes
      where id = class_id and teacher_id = auth.uid()
    )
  );

-- Create indexes
create index idx_classes_teacher on public.classes(teacher_id);
create index idx_classes_access_code on public.classes(access_code);
create index idx_class_students_class on public.class_students(class_id);
create index idx_class_students_student on public.class_students(student_id);

-- Function to generate unique access code
create or replace function generate_class_access_code()
returns text as $$
declare
  code text;
  exists boolean;
begin
  loop
    -- Generate 6-character alphanumeric code
    code := upper(substring(md5(random()::text) from 1 for 6));
    
    -- Check if code already exists
    select count(*) > 0 into exists
    from public.classes
    where access_code = code;
    
    exit when not exists;
  end loop;
  
  return code;
end;
$$ language plpgsql;
