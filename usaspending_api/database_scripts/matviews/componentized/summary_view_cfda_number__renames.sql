--------------------------------------------------------
-- Created using matview_sql_generator.py             --
--    The SQL definition is stored in a json file     --
--    Look in matview_generator for the code.         --
--                                                    --
--  DO NOT DIRECTLY EDIT THIS FILE!!!                 --
--------------------------------------------------------
ALTER MATERIALIZED VIEW IF EXISTS summary_view_cfda_number RENAME TO summary_view_cfda_number_old;
ALTER INDEX IF EXISTS idx_af8ca7ca$764_unique_pk RENAME TO idx_af8ca7ca$764_unique_pk_old;
ALTER INDEX IF EXISTS idx_af8ca7ca$764_action_date RENAME TO idx_af8ca7ca$764_action_date_old;
ALTER INDEX IF EXISTS idx_af8ca7ca$764_type RENAME TO idx_af8ca7ca$764_type_old;

ALTER MATERIALIZED VIEW summary_view_cfda_number_temp RENAME TO summary_view_cfda_number;
ALTER INDEX idx_af8ca7ca$764_unique_pk_temp RENAME TO idx_af8ca7ca$764_unique_pk;
ALTER INDEX idx_af8ca7ca$764_action_date_temp RENAME TO idx_af8ca7ca$764_action_date;
ALTER INDEX idx_af8ca7ca$764_type_temp RENAME TO idx_af8ca7ca$764_type;
