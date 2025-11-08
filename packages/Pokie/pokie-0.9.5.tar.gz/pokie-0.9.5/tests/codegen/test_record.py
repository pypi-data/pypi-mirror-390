import humps
from rick.form import RequestRecord, field

from pokie.codegen.pg import PgTableSpec
from pokie.codegen import RequestGenerator, RecordGenerator

record_tablespec = """
"""

record_tablespec_camel = """
"""

tablespec_serial_names = [
    "id_tablespec",
    "field_bigint",
    "field_bigserial",
    "field_bit",
    "field_varbit",
    "field_box",
    "field_bytea",
    "field_char",
    "field_varchar",
    "field_cidr",
    "field_circle",
    "field_date",
    "field_float8",
    "field_inet",
    "field_int4",
    "field_interval",
    "field_json",
    "field_jsonb",
    "field_line",
    "field_lseg",
    "field_macaddr",
    "field_macaddr8",
    "field_money",
    "field_numeric",
    "field_path",
    "field_point",
    "field_polygon",
    "field_float4",
    "field_int2",
    "field_smallserial",
    "field_text",
    "field_time",
    "field_timetz",
    "field_timestamp",
    "field_timestamptz",
    "field_tsquery",
    "field_tsvector",
    "field_uuid",
    "field_xml",
]


class TestRecordGenerator:
    def test_generate_source(self, pokie_db):
        pg_spec = PgTableSpec(pokie_db)
        spec = pg_spec.generate("tablespec_serial")
        generator = RecordGenerator()
        # default settings
        src = generator.generate_source(spec)
        assert self._cleanup(src) == self._cleanup(record_tablespec)

        # camelCase
        src = generator.generate_source(spec, camelcase=True)
        assert self._cleanup(src) == self._cleanup(record_tablespec_camel)

    def test_generate_class(self, pokie_db):
        pg_spec = PgTableSpec(pokie_db)
        spec = pg_spec.generate("tablespec_serial")
        generator = RecordGenerator()

        cls = generator.generate_class(spec)
        for name in tablespec_serial_names:
            if name == "id_tablespec":
                assert getattr(cls, "id") == name
            else:
                assert getattr(cls, name) == name

        cls = generator.generate_class(spec, camelcase=True)
        for name in tablespec_serial_names:
            if name == "id_tablespec":
                assert getattr(cls, "id") == name
            else:
                assert getattr(cls, humps.camelize(name)) == name

    def _cleanup(self, s: str):
        for c in ["\n", " "]:
            s = s.replace(c, "")
        return c
