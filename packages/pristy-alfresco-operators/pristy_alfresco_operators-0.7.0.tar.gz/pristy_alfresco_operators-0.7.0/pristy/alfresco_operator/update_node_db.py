# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0


def update_node_state_db(node: object, state: str, postgres_conn_id: str = "local_pg"):
    update_state_db(node["id"], state, postgres_conn_id=postgres_conn_id)


def update_state_db(
    child_id: str,
    state: str,
    table_name: str = "export_alfresco_folder_children",
    source_key: str = "uuid",
    postgres_conn_id: str = "local_pg",
):
    import logging
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    from psycopg2 import sql

    logger = logging.getLogger("airflow.task")
    logger.debug(f"Set node {child_id} to {state}")
    postgres_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    conn = postgres_hook.get_conn()
    cur = conn.cursor()
    try:
        # Utilisation de sql.Identifier pour les noms de table/colonne et paramètres pour les valeurs
        query = sql.SQL("UPDATE {table} SET state = %s WHERE {key} = %s").format(
            table=sql.Identifier(table_name), key=sql.Identifier(source_key)
        )
        cur.execute(query, (state, child_id))
        conn.commit()
        logger.debug("commit")
    finally:
        cur.close()
        conn.close()
