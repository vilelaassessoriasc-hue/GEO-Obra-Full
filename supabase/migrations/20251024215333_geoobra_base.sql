-- GEO-Obra • Migração base
-- Cria schema lógico, enum de status, tabela bruta e visões de agregados.

-- 1) Schema dedicado (mantém público limpo)
create schema if not exists geoobra;

-- 2) Enum de status compatível com seu coletor
do \$\$ begin
  if not exists (select 1 from pg_type where typname = 'task_status') then
    create type geoobra.task_status as enum ('pending','in_progress','done','blocked');
  end if;
end \$\$;

-- 3) Tabela bruta (dados coletados)
create table if not exists geoobra.tasks_raw (
  job_id        integer                        not null,
  task_id       bigint                         primary key,
  title         text                           not null,
  status        geoobra.task_status            not null,
  distance_km   numeric(10,2)                  null,     -- distância pode vir com vírgula; normalizamos ao inserir
  created_at    timestamptz                    not null
);

create index if not exists idx_tasks_raw_job    on geoobra.tasks_raw(job_id);
create index if not exists idx_tasks_raw_status on geoobra.tasks_raw(status);
create index if not exists idx_tasks_raw_date   on geoobra.tasks_raw((created_at::date));

-- 4) View: totais por dia (UTC)
create or replace view geoobra.v_tasks_per_day as
with norm as (
  select
    created_at at time zone 'UTC' as created_at_utc,
    status
  from geoobra.tasks_raw
)
select
  (created_at_utc::date) as date,
  count(*)               as total,
  count(*) filter (where status = 'pending')     as pending,
  count(*) filter (where status = 'in_progress') as in_progress,
  count(*) filter (where status = 'done')        as done,
  count(*) filter (where status = 'blocked')     as blocked
from norm
group by (created_at_utc::date)
order by (created_at_utc::date);

-- 5) View: distribuição por status
create or replace view geoobra.v_tasks_trend as
select
  status,
  count(*) as qty
from geoobra.tasks_raw
group by status
order by status;

-- 6) Permissões básicas (leitura pública — ajuste conforme sua política)
grant usage on schema geoobra to anon, authenticated;
grant select on all tables in schema geoobra to anon, authenticated;
grant select on all sequences in schema geoobra to anon, authenticated;
alter default privileges in schema geoobra grant select on tables to anon, authenticated;
