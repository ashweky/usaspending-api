--------------------------------------------------------
-- Created using matview_sql_generator.py             --
--    The SQL definition is stored in a json file     --
--    Look in matview_generator for the code.         --
--                                                    --
--  DO NOT DIRECTLY EDIT THIS FILE!!!                 --
--------------------------------------------------------
CREATE UNIQUE INDEX idx_78684541$f8b__unique_pk_temp ON summary_view_cfda_number_temp USING BTREE("pk") WITH (fillfactor = 97);
CREATE INDEX idx_78684541$f8b__action_date_temp ON summary_view_cfda_number_temp USING BTREE("action_date" DESC NULLS LAST) WITH (fillfactor = 97);
CREATE INDEX idx_78684541$f8b__type_temp ON summary_view_cfda_number_temp USING BTREE("action_date" DESC NULLS LAST, "type") WITH (fillfactor = 97);
CREATE INDEX idx_78684541$f8b__tuned_type_and_idv_temp ON summary_view_cfda_number_temp USING BTREE("type", "pulled_from") WITH (fillfactor = 97) WHERE "type" IS NULL AND "pulled_from" IS NOT NULL;
