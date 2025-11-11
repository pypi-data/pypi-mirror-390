import asyncio
from datetime import datetime  # noqa: F401

from orion.subscriber_matching.shipments_api import shipment_match_livin, shipment_match_villacruz  # noqa: F401
from orion.subscriber_matching.shipments_by_whabonnet import shipment_match_alquiventas, shipment_match_castillo  # noqa: F401


def shimpmets_suscribers(**kwargs):
    try:
        if asyncio.get_event_loop_policy().__class__.__name__ != "SelectorEventLoop":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except:
        pass

    #execution_date: datetime = kwargs.get("execution_date").time()
    #start_time = datetime.strptime("01-01-2024 14:00:00", "%d-%m-%Y %H:%M:%S").time()
    #end_time = datetime.strptime("01-01-2024 14:30:00", "%d-%m-%Y %H:%M:%S").time()
    #if start_time <= execution_date < end_time:
    #shipment_match_livin()

    shipment_match_villacruz()

    result = asyncio.run(shipment_match_castillo())
    print("*** result: ", result)

    result = asyncio.run(shipment_match_alquiventas())
    print("*** result: ", result)


if __name__ == "__main__":
    shimpmets_suscribers()