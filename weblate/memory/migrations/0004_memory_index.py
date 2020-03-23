# Generated by Django 3.0.4 on 2020-03-09 14:11

from django.db import migrations


def create_index(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor == "postgresql":
        schema_editor.execute(
            "CREATE INDEX memory_source_fulltext ON memory_memory "
            "USING GIN (to_tsvector('english', source))"
        )
        schema_editor.execute(
            "CREATE INDEX memory_source_index ON memory_memory USING HASH (source)"
        )
        schema_editor.execute(
            "CREATE INDEX memory_target_index ON memory_memory USING HASH (target)"
        )
        schema_editor.execute(
            "CREATE INDEX memory_origin_index ON memory_memory USING HASH (origin)"
        )
    elif vendor == "mysql":
        schema_editor.execute(
            "CREATE FULLTEXT INDEX memory_source_fulltext ON memory_memory(source)"
        )
        schema_editor.execute(
            "CREATE INDEX memory_lookup_index ON "
            "memory_memory(source(255), target(255), origin(255))"
        )
    else:
        raise Exception("Unsupported database: {}".format(vendor))


def drop_index(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor == "postgresql":
        schema_editor.execute("DROP INDEX memory_source_fulltext")
        schema_editor.execute("DROP INDEX memory_source_index")
        schema_editor.execute("DROP INDEX memory_target_index")
        schema_editor.execute("DROP INDEX memory_origin_index")
    elif vendor == "mysql":
        schema_editor.execute(
            "ALTER TABLE memory_memory DROP INDEX memory_source_fulltext"
        )
        schema_editor.execute(
            "ALTER TABLE memory_memory DROP INDEX memory_lookup_index"
        )
    else:
        raise Exception("Unsupported database: {}".format(vendor))


class Migration(migrations.Migration):

    dependencies = [("memory", "0003_migrate_memory")]

    # This can't be atomic on MySQL
    operations = [
        migrations.RunPython(create_index, drop_index, elidable=False, atomic=False)
    ]
