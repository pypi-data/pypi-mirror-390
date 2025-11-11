from orion.databases.db_bellatrix.repositories.query_acrecer import MLSAcrecer, QuerysMLSAcrecer  # noqa: F401
from orion.searcher.properties.transform_data_mls_acrecer import parse_bathrooms  # noqa: F401
from orion.tools import df_to_dicts, list_obj_to_df, parse_features  # noqa: F401


# parse_bathrooms
def main():
    mls_acrecer = QuerysMLSAcrecer.select_all()
    mls_acrecer = list_obj_to_df(mls_acrecer)

    mls_acrecer["bano_social"] = mls_acrecer["householdFeatures"].apply(lambda x: parse_features(x).get("Baño social"))

    mls_acrecer["bedrooms"] = mls_acrecer["numberOfRooms"].fillna(0).astype(int)
    mls_acrecer["bathrooms"] = mls_acrecer["rooms"].apply(lambda x: parse_features(x).get("baths"))
    mls_acrecer["bathrooms"]= mls_acrecer["bathrooms"].fillna(0).astype(int)

    #mls_acrecer["bathrooms_t"] = mls_acrecer["bathrooms"].apply(lambda x: parse_bathrooms(x))
    mls_acrecer["elevator"] = mls_acrecer["inCondominiumFeatures"].apply(lambda x: parse_features(x).get("servedByElevator"))
    mls_acrecer["garage"] = mls_acrecer["householdFeatures"].apply(lambda x: parse_features(x).get("garages"))
    mls_acrecer["neighborhood"] = mls_acrecer["locationData"].apply(lambda x: parse_features(x).get("neighborhood"))

    mls_acrecer["elevator"] = mls_acrecer["elevator"].replace("T", True).fillna(False)
    mls_acrecer["garage"] = mls_acrecer["garage"].fillna(0).astype(int)

    print(mls_acrecer[["numberOfRooms", "rooms", "bedrooms", "bathrooms"]])
    print(mls_acrecer[["householdFeatures", "bano_social", "elevator", "garage", "neighborhood"]])


if __name__ == "__main__":
    main()
