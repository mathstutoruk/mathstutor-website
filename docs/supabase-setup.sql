-- mathstutor.co.uk accounts: run once in Supabase > SQL Editor.
-- Creates student and parent profiles, a parent-to-student link,
-- and row-level security so each person only sees their own data
-- (and a parent sees only the students they have linked).

create table if not exists public.profiles (
  id          uuid primary key references auth.users(id) on delete cascade,
  role        text not null check (role in ('student','parent')),
  first_name  text not null default '',
  last_name   text not null default '',
  course      text,
  link_code   text unique,
  created_at  timestamptz not null default now()
);

create table if not exists public.parent_links (
  parent_id   uuid not null references public.profiles(id) on delete cascade,
  student_id  uuid not null references public.profiles(id) on delete cascade,
  created_at  timestamptz not null default now(),
  primary key (parent_id, student_id)
);

alter table public.profiles enable row level security;
alter table public.parent_links enable row level security;

-- People can read and update their own profile (but not change their role or code).
create policy "read own profile" on public.profiles
  for select using (auth.uid() = id);
create policy "update own course and name" on public.profiles
  for update using (auth.uid() = id)
  with check (auth.uid() = id);
revoke update on public.profiles from authenticated;
grant update (first_name, last_name, course) on public.profiles to authenticated;

-- Parents can see their own links.
create policy "parents read own links" on public.parent_links
  for select using (auth.uid() = parent_id);

-- New sign-ups get a profile automatically, using the details from the form.
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
declare
  r text := coalesce(new.raw_user_meta_data->>'role', 'student');
begin
  if r not in ('student','parent') then r := 'student'; end if;
  insert into public.profiles (id, role, first_name, last_name, course, link_code)
  values (
    new.id, r,
    left(coalesce(new.raw_user_meta_data->>'first_name', ''), 80),
    left(coalesce(new.raw_user_meta_data->>'last_name', ''), 80),
    case when r = 'student' then nullif(new.raw_user_meta_data->>'course', '') end,
    case when r = 'student' then upper(substr(md5(gen_random_uuid()::text), 1, 6)) end
  );
  return new;
end $$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- A parent links a student by entering the student's 6-character code.
create or replace function public.link_child(code text)
returns void language plpgsql security definer set search_path = public as $$
declare
  me public.profiles;
  kid uuid;
begin
  select * into me from public.profiles where id = auth.uid();
  if me.role is distinct from 'parent' then raise exception 'Only parent accounts can link a student'; end if;
  select id into kid from public.profiles where link_code = upper(trim(code)) and role = 'student';
  if kid is null then raise exception 'No student with that code'; end if;
  insert into public.parent_links (parent_id, student_id) values (me.id, kid) on conflict do nothing;
end $$;

-- A parent's linked students (name and course only).
create or replace function public.my_children()
returns table (first_name text, last_name text, course text)
language sql security definer set search_path = public as $$
  select p.first_name, p.last_name, p.course
  from public.parent_links l join public.profiles p on p.id = l.student_id
  where l.parent_id = auth.uid()
  order by p.first_name;
$$;

revoke all on function public.link_child(text) from public, anon;
revoke all on function public.my_children() from public, anon;
grant execute on function public.link_child(text) to authenticated;
grant execute on function public.my_children() to authenticated;
