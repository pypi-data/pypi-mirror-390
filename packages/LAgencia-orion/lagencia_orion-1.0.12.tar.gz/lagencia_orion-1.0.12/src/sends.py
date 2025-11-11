import time

from sqlalchemy.sql.expression import and_

from orion.databases.config_db_empatia import get_session_empatia
from orion.databases.db_empatia.repositories.querys_searcher import NewRevenues, Property, Subscriptions
from orion.journey.templates import Category, TemplatesForLessThan45Days, TemplatesForMoreThan90Days, TemplatesForRange45AND90Days
from orion.journey.tools_sends_by_meta import RequestAPIMeta, SendMessageByAPIMeta  # noqa: F401

if __name__ == "__main__":
    REAL_ESTATE = "castillo"

    with get_session_empatia() as session:
        # Realizar la consulta
        result = (
            session.query(Property.id, Property.code, Property.price, Property.old_price, Subscriptions.mobile, Subscriptions.token, Subscriptions.week_noti, Subscriptions.option)
            .join(NewRevenues, NewRevenues.property_id == Property.id)
            .join(Subscriptions, Subscriptions.id == NewRevenues.subscription_id)
            .where(and_(Subscriptions.website == REAL_ESTATE, Subscriptions.week_noti.isnot(None)))
            .all()
        )

    for row in result:
        print(row)

    # phone=record[4]
    records = [RequestAPIMeta(code=record[1], phone="573165241659", token=record[5], price=record[2], old_price=record[3], week=record[6], option=record[7]) for record in result]
    print(len(records))

    for record in records:
        if (record.option == Category.LESS_THAN_45) and record.week:
            templates = TemplatesForLessThan45Days.get(record.week)

        if (record.option == Category.MORE_THAN_90) and record.week:
            templates = TemplatesForMoreThan90Days.get(record.week)

        if (record.option == Category.BETWEEN_45_AND_90) and record.week:
            templates = TemplatesForRange45AND90Days.get(record.week)

        service = SendMessageByAPIMeta(templates=templates, record=record)
        service.send()
        time.sleep(2)
