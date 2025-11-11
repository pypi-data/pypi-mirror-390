from typing import List

from orion.databases.db_empatia.repositories.querys_searcher import QuerysSubscriptions, Subscriptions


class Category:
    LESS_THAN_45 = "-45"
    BETWEEN_45_AND_90 = "45-90"
    MORE_THAN_90 = "+90"


class TemplatesForLessThan45Days:
    week_1: List[str] = ["nuevos_ingresos", "modifica_precio"]
    week_2: List[str] = ["nuevos_ingresos", "modifica_precio"]
    week_3: List[str] = ["nuevos_ingresos", "modifica_precio"]
    week_4: List[str]
    week_5: List[str]
    week_6: List[str]

    @classmethod
    def get(cls, week: int) -> List[str]:
        return getattr(cls, f"week_{week}")


class TemplatesForRange45AND90Days:
    week_1: List[str] = ["nuevo_ingreso", "45a90_dias_semana1"]
    week_2: List[str] = ["nuevo_ingreso"]
    week_3: List[str] = ["nuevo_ingreso"]
    week_4: List[str] = ["nuevo_ingreso"]
    week_5: List[str] = ["nuevo_ingreso", "art_est_arrend"]
    week_6: List[str] = ["nuevo_ingreso"]
    week_7: List[str] = ["nuevos_ingresos", "modifica_precio"]
    week_8: List[str] = ["nuevos_ingresos", "modifica_precio"]
    week_9: List[str] = ["nuevos_ingresos", "modifica_precio", "import_contrato"]
    week_10: List[str]
    week_11: List[str]
    week_12: List[str]

    @classmethod
    def get(cls, week: int) -> List[str]:
        return getattr(cls, f"week_{week}")


class TemplatesForMoreThan90Days:
    week_1: List[str] = ["nuevo_ingreso", "45a90_dias_semana1"]
    week_2: List[str] = ["nuevo_ingreso"]
    week_3: List[str] = ["nuevo_ingreso"]
    week_4: List[str] = ["nuevo_ingreso"]
    week_5: List[str] = ["nuevo_ingreso", "art_est_arrend"]
    week_6: List[str] = ["nuevo_ingreso"]
    week_7: List[str] = ["nuevo_ingreso"]
    week_8: List[str] = ["nuevo_ingreso"]
    week_9: List[str] = ["nuevos_ingresos", "modifica_precio", "import_contrato"]
    week_10: List[str] = ["nuevos_ingresos", "modifica_precio"]
    week_11: List[str] = ["nuevos_ingresos", "modifica_precio"]
    week_12: List[str]
    week_13: List[str]
    week_14: List[str]
    week_15: List[str]
    week_16: List[str]
    week_17: List[str]
    week_18: List[str]

    @classmethod
    def get(cls, week: int) -> List[str]:
        return getattr(cls, f"week_{week}")


if __name__ == "__main__":
    tools = QuerysSubscriptions()
    records = tools.select_by_filter(Subscriptions.send_noti == 0)
    print(records)

    ...
