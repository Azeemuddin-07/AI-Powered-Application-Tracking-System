"""Create the custom-user tables needed before Django's admin migration.

The project intentionally has no checked-in migrations for its local apps.
On a brand-new PostgreSQL database, Django's admin migration references the
custom user model before ``migrate --run-syncdb`` gets a chance to create it.
Render invokes this module after the built-in auth migrations and before the
normal sync step so a fresh deployment can bootstrap safely.
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.db import connection

from apps.accounts.models import AuditLog, User


def main() -> None:
    existing_tables = set(connection.introspection.table_names())
    models = (User, AuditLog)

    with connection.schema_editor() as schema_editor:
        for model in models:
            if model._meta.db_table not in existing_tables:
                schema_editor.create_model(model)


if __name__ == "__main__":
    main()
