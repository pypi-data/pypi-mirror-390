from datetime import datetime, timezone
from typing import List

import pandas as pd
from loguru import logger

from orion.acrecer.acrecer import get_all_properties_acrecer_by_city_sync
from orion.databases.config_db_bellatrix import get_session_bellatrix
from orion.databases.db_bellatrix.models.model_acrecer import MLSAcrecer
from orion.databases.db_bellatrix.repositories.query_acrecer import QuerysMLSAcrecer
from orion.definition_ids import ID_BASE_MLS_ACRECER
from orion.tools import df_to_dicts, list_obj_to_df

"""Configuración del módulo

Contiene funciones para extraer, transformar y cargar propiedades desde
el servicio MLS Acrecer. El archivo fue documentado en español y se
añadieron logs con `loguru` para mejorar trazabilidad. NO se ha cambiado
la lógica del código original.
"""


def split_by_type_transaccion(): ...


def format_dates(date: str):
    return datetime.fromisoformat(date.replace("T", " ")).date().strftime("%Y-%m-%d %H:%M:%S")


def to_mysql_dt(s: str):
    if s is None or str(s).strip() == "":
        return None
    dt = datetime.fromisoformat(str(s).replace("Z", "+00:00"))  # aware UTC
    # guardar en UTC sin tzinfo (válido para columna DATETIME)
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


def load_data_for_table_acrecer():
    logger.info("load_data_for_table_acrecer: inicio")
    new_data_acrecer = get_all_properties_acrecer_by_city_sync()
    if new_data_acrecer is None:
        logger.warning("load_data_for_table_acrecer: no se obtuvo nueva data, abortando carga")
        return


    new_data_acrecer["prefix_code"] = new_data_acrecer["code"].apply(lambda x: str(x).split("-")[0] if "-" in str(x) else None)
    new_data_acrecer["code"] = new_data_acrecer["code"].apply(lambda x: str(x).split("-")[1] if "-" in str(x) else x)
    new_data_acrecer["id"] = new_data_acrecer["code"].astype(int).copy()
    new_data_acrecer["id"] = new_data_acrecer["id"] + ID_BASE_MLS_ACRECER
    new_data_acrecer["propertyImages"] = new_data_acrecer["propertyImages"].astype(str)
    new_data_acrecer["active"] = True
    new_data_acrecer["source"] = "mls_acrecer"
    new_data_acrecer.drop_duplicates(subset=["id"], inplace=True)
    new_data_acrecer = new_data_acrecer[new_data_acrecer["id"].notnull()]
    new_data_acrecer["addedOn"] = new_data_acrecer["addedOn"].map(to_mysql_dt)
    new_data_acrecer["lastUpdate"] = new_data_acrecer["lastUpdate"].map(to_mysql_dt)

    new_data_acrecer_t = new_data_acrecer.copy()

    with get_session_bellatrix() as session:
        result: List[MLSAcrecer] = session.query(MLSAcrecer).where(MLSAcrecer.active == 1).all()
        table_acrecer = list_obj_to_df(result)

    if not table_acrecer.empty and not new_data_acrecer_t.empty:
        merge = table_acrecer.merge(new_data_acrecer_t, on="id", how="outer", suffixes=("_db", "_api"), indicator=True)

        merge = merge[["id", "lastUpdate_db", "lastUpdate_api", "addedOn_db", "addedOn_api", "_merge"]]

        date_cols = ["lastUpdate_db", "addedOn_db", "lastUpdate_api", "addedOn_api"]
        for col in date_cols:
            merge.loc[:, col] = pd.to_datetime(merge[col], errors="coerce").dt.tz_localize(None)

        merge_inner = merge[merge["_merge"] == "both"]
        ids_by_update = merge_inner.loc[merge_inner["lastUpdate_api"] > merge_inner["lastUpdate_db"], "id"]
        ids_by_update = set(ids_by_update)
        merge_update = new_data_acrecer_t[new_data_acrecer_t["id"].isin(ids_by_update)]

        merge_left_only = merge[merge["_merge"] == "left_only"]
        ids_by_delete = merge_left_only["id"]
        merge_delete = table_acrecer[table_acrecer["id"].isin(ids_by_delete.to_list())]

        merge_right_only = merge[merge["_merge"] == "right_only"]
        ids_by_insert = merge_right_only["id"]
        merge_insert = new_data_acrecer_t[new_data_acrecer_t["id"].isin(ids_by_insert.to_list())]

    elif table_acrecer.empty:
        merge_update = pd.DataFrame()
        merge_delete = pd.DataFrame()
        merge_insert = new_data_acrecer_t.copy()

    elif new_data_acrecer_t.empty:
        merge_update = pd.DataFrame()
        merge_delete = pd.DataFrame()
        merge_insert = pd.DataFrame()

    logger.info("load_data_for_table_acrecer: merge_update filas=%s merge_delete filas=%s merge_insert filas=%s", len(merge_update), len(merge_delete), len(merge_insert))

    if not merge_update.empty:
        records = df_to_dicts(merge_update)
        QuerysMLSAcrecer.upsert_all(records)

    if not merge_delete.empty:
        records = df_to_dicts(merge_delete)
        for record in records:
            QuerysMLSAcrecer.delete_by_id(record.get("id"))

    if not merge_insert.empty:
        records = df_to_dicts(merge_insert)
        QuerysMLSAcrecer.bulk_insert(records)


if __name__ == "__main__":
    ...
