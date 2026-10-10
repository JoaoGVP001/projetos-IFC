-- Add missing RLS policies for question_options
-- This allows teachers to create question options when creating questions

create policy "Teachers can create question options"
  on public.question_options for insert
  with check (
    exists (
      select 1 from public.profiles
      where id = auth.uid() and role = 'teacher'
    )
  );

create policy "Teachers can update question options"
  on public.question_options for update
  using (
    exists (
      select 1 from public.profiles
      where id = auth.uid() and role = 'teacher'
    )
  );

create policy "Teachers can delete question options"
  on public.question_options for delete
  using (
    exists (
      select 1 from public.profiles
      where id = auth.uid() and role = 'teacher'
    )
  );
