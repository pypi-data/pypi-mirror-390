from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List
import pandas as pd

from src.database.config_db import get_session
from src.database.models.model_searcher import Property, Subscriptions, NewRevenues
from src.database.repository.querys_searcher import QuerysNewRevenues, QuerysSubscriptions, QuerysSector, QuerysPropertySector, QuerysProperty
from src.tools import list_obj_to_df, df_to_dicts

from itertools import product
import json
import os
from datetime import datetime, timezone


def get_all_Subscriptions()->pd.DataFrame:

    """"
    Consulta la tabla Subscriptions y retorna un df con los datos procesados
    """

    path= os.path.join(os.path.dirname(__file__), "..", "..", "outputs", "match_suscribers")

    # obtenemos suscriptores no vencidos
    suscribers= QuerysSubscriptions.select_by_filter(Subscriptions.end_date >= datetime.now().date())


    subscriptions= []
    for suscriber in suscribers:
        subs_data= {}
        filters= {}
        dates= {}
        others= {}
        subs_data.update({"id": suscriber.id})
        subs_data.update({"name": suscriber.name})
        subs_data.update({"mobile" : suscriber.mobile})
        subs_data.update({"email" :suscriber.email})
        filters.update({"slug_sectors": suscriber.slug_sectors.split("|") if suscriber.slug_sectors else None})
        filters.update({"management": suscriber.management})
        filters.update({"property_types": suscriber.property_types.split("|") if suscriber.property_types else None})
        filters.update({"bedrooms": suscriber.bedrooms.split("|") if suscriber.bedrooms else None})
        filters.update({"bathrooms": suscriber.bathrooms.split("|") if suscriber.bathrooms else None})
        filters.update({"garages": suscriber.garages.split("|") if suscriber.garages else None})

        filters.update({"price" : suscriber.price.split("-") if suscriber.price else [None, None]})
        filters.update({"price_min": filters.get("price")[0]})
        filters.update({"price_max": filters.get("price")[1]})
        del filters["price"]

        dates.update({"start_date" : suscriber.start_date})
        dates.update({"end_date" : suscriber.end_date})
        dates.update({"created_at" : suscriber.created_at})
        dates.update({"updated_at" : suscriber.updated_at})
        others.update({"website" : suscriber.website})

        # convertir cada key del dic en list
        for key, value in filters.items():
            if not isinstance(filters[key], list):
                filters[key]= [value]

        # combinacion de todos los filtros para obtener todas las posibles opciones de propiedades
        keys= filters.keys()
        values= filters.values()
        combinations= list(product(*values))
        results= [dict(zip(keys, combination)) for combination in combinations]

        for result in results:
            result.update(subs_data)
            result.update(dates)
            result.update(others)

        subscriptions+= results

    subscriptions= pd.DataFrame(subscriptions)

    subscriptions["start_date"] = pd.to_datetime(subscriptions["start_date"])
    subscriptions["end_date"] = pd.to_datetime(subscriptions["end_date"])
    subscriptions["waiting_days"] = (subscriptions["end_date"] - subscriptions["start_date"]).dt.days

    suscribers= subscriptions.sort_values(by=["waiting_days"]).copy()

    if suscribers.empty:
        return suscribers

    current_date= pd.to_datetime(datetime.now().date())
    candidates= pd.DataFrame(columns=suscribers.columns)
    ids= []
    for index, row in suscribers.iterrows():
        if not (row["start_date"] <= current_date <= row["end_date"]):
            continue
        ids+=[index]
    candidates= suscribers.iloc[ids, :].copy()

    candidates = candidates.replace("", None).copy()
    candidates = candidates.replace(np.nan, None).copy()

    return candidates


def match(candidates: pd.DataFrame)-> List[pd.DataFrame]:

    path= os.path.join(os.path.dirname(__file__), "..", "..", "outputs", "match_suscribers")

    candidates= candidates[candidates["waiting_days"] <= 45 ].copy()
    candidates.rename(columns={"id":"candidates_id"}, inplace= True)

    #obtener todos los sectores
    records= QuerysSector.select_all()
    sectors= list_obj_to_df(records)
    sectors= sectors[["id", "slug"]]
    merged= candidates.merge(sectors, how="inner", left_on="slug_sectors", right_on="slug")
    merged.rename(columns={"id": "sector_id"}, inplace= True)

    # consultar tabla property_sectors y hacer merge con los candidatos
    records= QuerysPropertySector.select_all()
    property_sector= list_obj_to_df(records)
    merged= merged.merge(property_sector, how="inner", on="sector_id")
    merged.drop(columns=["id"], inplace= True)


    # !!! considerar añadir end_date para la eliminacion de los vencidos
    merged= merged[["candidates_id",
                    "sector_id",
                    "property_id",
                    "slug_sectors",
                    "website",
                    "management",
                    "property_types",
                    "bedrooms",
                    "bathrooms",
                    "garages",
                    "price_max",
                    "price_min",
                    "name",
                    "mobile",
                    "email"
                    ]]


    date= datetime.now().date() # yyyy-mm-dd propiedades del mismo dia
    #date= datetime.strptime("2025-04-09", "%Y-%m-%d").date()
    records= QuerysProperty.select_by_filter(Property.created_at>=date)
    propertes= list_obj_to_df(records)
    if propertes.empty:
        df_empty= pd.DataFrame()
        return [df_empty, df_empty, df_empty, df_empty]

    propertes= propertes[["id",
                            "show_villacruz",
                            "show_castillo",
                            "show_estrella",
                            "show_livin",
                            "management",
                            "property_type_searcher",
                            "bedrooms",
                            "bathrooms",
                            "garage",
                            "price",
                            "code",
                            "modified_date",
                            "created_at"
                        ]]



    merged= merged.merge(propertes, how="inner", left_on="property_id", right_on="id")

    merged.drop_duplicates(subset=["candidates_id", "sector_id", "property_id"], inplace= True)
    merged.to_excel(os.path.join(path, "match_sin_filtros.xlsx"), index=False)



    # # !!! falta agregar procesamiento por imobiliaria
    merged["bedrooms_x"]= merged["bedrooms_x"].apply(lambda x: int(x) if pd.notna(x) else x)
    merged["bedrooms_y"]= merged["bedrooms_y"].apply(lambda x: int(x) if pd.notna(x) else x)
    isnull= merged[merged["bedrooms_x"].isnull()]
    isnull["status_bedrooms"]= True
    notnull= merged[merged["bedrooms_x"].notnull()]
    notnull["status_bedrooms"]= notnull["bedrooms_x"]==notnull["bedrooms_y"]
    mask = notnull["bedrooms_x"] == 5
    notnull.loc[mask, "status_bedrooms"] = notnull.loc[mask, "bedrooms_y"] >= 5
    merged= pd.concat([notnull, isnull])

    merged["bathrooms_x"]= merged["bathrooms_x"].apply(lambda x: int(x) if pd.notna(x) else x)
    merged["bathrooms_y"]= merged["bathrooms_y"].apply(lambda x: int(x) if pd.notna(x) else x)
    isnull= merged[merged["bathrooms_x"].isnull()]
    isnull["status_bathrooms"]= True
    notnull= merged[merged["bathrooms_x"].notnull()]
    notnull["status_bathrooms"]= notnull["bathrooms_x"]==notnull["bathrooms_y"]
    # Ajuste cuando bathrooms_x == 5
    mask = notnull["bathrooms_x"] == 5
    notnull.loc[mask, "status_bathrooms"] = notnull.loc[mask, "bathrooms_y"] >= 5
    merged= pd.concat([notnull, isnull])


    merged["garages"]= merged["garages"].apply(lambda x: int(x) if pd.notna(x) else x)
    merged["garage"]= merged["garage"].apply(lambda x: int(x) if pd.notna(x) else x)
    isnull= merged[merged["garages"].isnull()]
    isnull["status_garage"]= True
    notnull= merged[merged["garages"].notnull()]
    notnull["status_garage"]= notnull["garages"]==notnull["garage"]
    mask = notnull["garages"] == 5
    notnull.loc[mask, "status_garage"] = notnull.loc[mask, "garage"] >= 5
    merged= pd.concat([notnull, isnull])


    merged["price"]= merged["price"].apply(lambda x: float(x) if pd.notna(x) else x)
    merged["price_min"]= merged["price_min"].apply(lambda x: float(x) if pd.notna(x) else x)
    merged["price_max"]= merged["price_max"].apply(lambda x: float(x) if pd.notna(x) else x)
    isnull= merged[merged["price"].isnull()]
    isnull["status_price"]= True
    notnull= merged[merged["price"].notnull()]
    notnull["status_price"]= notnull.apply(lambda x: x["price_min"] <= x["price"] <= x["price_max"], axis=1)
    merged= pd.concat([notnull, isnull])

    isnull= merged[merged["management_x"].isnull()]
    isnull["status_management"]= True
    notnull= merged[merged["management_x"].notnull()]
    notnull["status_management"]= notnull["management_x"]==notnull["management_y"]
    merged= pd.concat([notnull, isnull])

    notnull= merged[merged["property_types"].notnull()]
    notnull["status_property_types"]= notnull["property_types"]==notnull["property_type_searcher"]
    isnull= merged[merged["property_types"].isnull()]
    isnull["status_property_types"]= True
    merged= pd.concat([notnull, isnull])

    merged.to_excel(os.path.join(path, "revisar.xlsx"), index=False)



    merged= merged.loc[(merged["status_management"] & merged["status_property_types"] & merged["status_bedrooms"]
           & merged["status_bathrooms"] &  merged["status_garage"] & merged["status_price"])]

    merged.drop_duplicates(subset=["candidates_id", "property_id"], inplace= True)

    candidates_livin = merged[(merged["show_livin"]) & (merged["website"] == "livin")]
    candidates_estrella = merged[(merged["show_estrella"]) & (merged["website"] == "estrella")]
    candidates_castillo = merged[(merged["show_castillo"]) & (merged["website"] == "castillo")]
    candidates_villacruz = merged[(merged["show_villacruz"]) & (merged["website"] == "villacruz")]

    merged.to_excel(os.path.join(path, "match.xlsx"), index=False)
    return [candidates_livin, candidates_estrella, candidates_castillo, candidates_villacruz]


def load_match(new_matches: pd.DataFrame):

    if new_matches.empty:
        return

    new_matches= new_matches[["candidates_id", "property_id"]].rename(columns= {"candidates_id": "subscription_id"}).copy()

    records= QuerysNewRevenues.select_all()
    new_revenues= list_obj_to_df(records)
    merged= new_matches.merge(new_revenues, how="outer", on=["subscription_id", "property_id"], indicator=True)

    left_merged= merged[merged["_merge"]=="left_only"]

    if not left_merged.empty:

        id_to_delete = left_merged["subscription_id"].unique()

        for id_ in id_to_delete:
            QuerysNewRevenues.delete_by_filter(NewRevenues.subscription_id == id_)

        left_merged["notified"]= False
        left_merged["created_at"]= datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        left_merged.drop(columns=["_merge"], inplace=True)

        records= df_to_dicts(left_merged)
        QuerysNewRevenues.bulk_insert(records)

if __name__=="__main__":

    candidates= get_all_Subscriptions()
    print(candidates)
    candidates_livin, candidates_estrella, candidates_castillo, candidates_villacruz= match(candidates)
    candidates_livin.to_excel("candidates_livin.xlsx", index=False)
    print(candidates_livin)




