"""Cliente API para el servicio MLS Acrecer.

Este módulo proporciona funcionalidades para consultar propiedades
del servicio MLS Acrecer usando requests asíncronos con httpx.
"""

import asyncio
from typing import Any, Dict, List, Optional

import httpx
import pandas as pd
from loguru import logger

from orion.acrecer.permmited_cities import CIUDADES
from orion import config


class AcrecerAPIError(Exception):
    """Excepción personalizada para errores de la API de Acrecer."""

    ...


class AcrecerAuthService:
    """Servicio de autenticación para MLS Acrecer."""

    BASE_URL = "https://mls.mbp.com.co/mobilia-mls/ws"

    def __init__(self, subject: Optional[str] = None):
        """Inicializa el servicio de autenticación.

        Parameters
        ----------
        subject : str, optional
            Subject para autenticación. Si no se proporciona, se lee de variables de entorno.
        """
        self.subject = subject or config.SUBJECT_MLS_ACRECER
        if not self.subject:
            raise ValueError("SUBJECT_MLS_ACRECER no está configurado")

        logger.debug("AcrecerAuthService inicializado con subject: {}", self.subject[:10] + "...")

    async def get_jwt_token(self, client: httpx.AsyncClient) -> str:
        """Obtiene el token JWT para autenticación.

        Parameters
        ----------
        client : httpx.AsyncClient
            Cliente HTTP asíncrono para realizar la petición.

        Returns
        -------
        str
            Token JWT válido.

        Raises
        ------
        AcrecerAPIError
            Si no se puede obtener el token.
        """
        url = f"{self.BASE_URL}/Auth"
        params = {"operation": "getAccessJWToken", "subject": self.subject}

        logger.info("Solicitando token JWT...")

        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()

            data = response.json()
            jwt_token = data.get("JWT")

            if not jwt_token:
                raise AcrecerAPIError("No se recibió token JWT en la respuesta")

            logger.success("Token JWT obtenido exitosamente")
            return jwt_token

        except httpx.HTTPStatusError as e:
            logger.error("Error HTTP al obtener token: {} - {}", e.response.status_code, e.response.text)
            raise AcrecerAPIError(f"Error al obtener token JWT: {e}") from e
        except httpx.RequestError as e:
            logger.error("Error de conexión al obtener token: {}", str(e))
            raise AcrecerAPIError(f"Error de conexión: {e}") from e
        except Exception as e:
            logger.exception("Error inesperado al obtener token JWT")
            raise AcrecerAPIError(f"Error inesperado: {e}") from e


class AcrecerPropertiesService:
    """Servicio para consultar propiedades de MLS Acrecer."""

    BASE_URL = "https://mls.mbp.com.co/mobilia-mls/ws/Properties"
    DEFAULT_RECORDS_PER_PAGE = 30
    REQUEST_DELAY = 0.3  # Segundos entre peticiones

    def __init__(self, jwt_token: str):
        """Inicializa el servicio de propiedades.

        Parameters
        ----------
        jwt_token : str
            Token JWT válido para autenticación.
        """
        self.jwt_token = jwt_token
        self.headers = {"Authorization": f"Bearer {jwt_token}", "Accept": "application/json"}
        logger.debug("AcrecerPropertiesService inicializado")

    async def fetch_properties_page(self, client: httpx.AsyncClient, city: str, page: int, records_per_page: int = DEFAULT_RECORDS_PER_PAGE) -> List[Dict[str, Any]]:
        """Obtiene una página de propiedades para una ciudad específica.

        Parameters
        ----------
        client : httpx.AsyncClient
            Cliente HTTP asíncrono.
        city : str
            Nombre de la ciudad a consultar.
        page : int
            Número de página a consultar.
        records_per_page : int, optional
            Cantidad de registros por página (default: 30).

        Returns
        -------
        List[Dict[str, Any]]
            Lista de propiedades encontradas en la página.
        """
        params = {
            "operation": "publicPropertiesSearchByCityZone",
            "cityName": city,
            "page": str(page),
            "recordsPerPage": str(records_per_page),
        }

        try:
            response = await client.get(self.BASE_URL, params=params, headers=self.headers, timeout=30.0)

            logger.info("Petición a API - ciudad: {}, página: {}, status: {}", city, page, response.status_code)

            response.raise_for_status()

            data = response.json()
            results = data.get("searchResults", [])

            # Agregar información de la ciudad a cada resultado
            for result in results:
                result["ciudad"] = city

            logger.debug("Resultados obtenidos: {} propiedades (ciudad: {}, página: {})", len(results), city, page)

            return results

        except httpx.HTTPStatusError as e:
            logger.error("Error HTTP en ciudad: {}, página: {} - Status: {}, Response: {}", city, page, e.response.status_code, e.response.text[:200])
            return []
        except httpx.RequestError as e:
            logger.error("Error de conexión en ciudad: {}, página: {} - {}", city, page, str(e))
            return []
        except Exception:
            logger.exception("Error inesperado procesando ciudad: {}, página: {}", city, page)
            return []

    async def fetch_all_properties_for_city(self, client: httpx.AsyncClient, city: str) -> List[Dict[str, Any]]:
        """Obtiene todas las propiedades de una ciudad (paginación completa).

        Parameters
        ----------
        client : httpx.AsyncClient
            Cliente HTTP asíncrono.
        city : str
            Nombre de la ciudad a consultar.

        Returns
        -------
        List[Dict[str, Any]]
            Lista con todas las propiedades de la ciudad.
        """
        logger.info("Iniciando consulta para ciudad: {}", city)

        all_properties = []
        page = 1

        while True:
            properties = await self.fetch_properties_page(client=client, city=city, page=page)

            if not properties:
                logger.info("Fin de paginación para ciudad: {} (página: {})", city, page)
                break

            all_properties.extend(properties)

            # Si recibimos menos registros que el máximo, es la última página
            if len(properties) < self.DEFAULT_RECORDS_PER_PAGE:
                logger.info("Última página alcanzada para ciudad: {} (total: {} propiedades)", city, len(all_properties))
                break

            page += 1

            # Delay para no saturar la API
            await asyncio.sleep(self.REQUEST_DELAY)

        logger.success("Consulta completada para ciudad: {} - Total propiedades: {}", city, len(all_properties))

        return all_properties


class AcrecerClient:
    """Cliente principal para interactuar con la API de MLS Acrecer."""

    def __init__(self, subject: Optional[str] = None):
        """Inicializa el cliente de Acrecer.

        Parameters
        ----------
        subject : str, optional
            Subject para autenticación.
        """
        self.auth_service = AcrecerAuthService(subject=subject)
        self.properties_service: Optional[AcrecerPropertiesService] = None
        logger.info("AcrecerClient inicializado")

    async def initialize(self, client: httpx.AsyncClient):
        """Inicializa el cliente obteniendo el token JWT.

        Parameters
        ----------
        client : httpx.AsyncClient
            Cliente HTTP asíncrono.
        """
        jwt_token = await self.auth_service.get_jwt_token(client)
        self.properties_service = AcrecerPropertiesService(jwt_token=jwt_token)
        logger.info("AcrecerClient autenticado exitosamente")

    async def get_all_properties_by_cities(self, cities: List[str]) -> pd.DataFrame:
        """Obtiene todas las propiedades para múltiples ciudades.

        Parameters
        ----------
        cities : List[str]
            Lista de nombres de ciudades a consultar.

        Returns
        -------
        pd.DataFrame
            DataFrame con todas las propiedades encontradas.

        Raises
        ------
        AcrecerAPIError
            Si ocurre un error durante la consulta.
        """
        logger.info("Iniciando consulta para {} ciudades", len(cities))

        async with httpx.AsyncClient() as client:
            # Inicializar y autenticar
            await self.initialize(client)

            if not self.properties_service:
                raise AcrecerAPIError("Properties service no inicializado")

            # Consultar todas las ciudades
            all_properties = []

            for city in cities:
                properties = await self.properties_service.fetch_all_properties_for_city(client=client, city=city)
                all_properties.extend(properties)

            logger.success("Consulta completada - Total propiedades: {} de {} ciudades", len(all_properties), len(cities))

            # Convertir a DataFrame
            if all_properties:
                df = pd.DataFrame(all_properties)
                logger.info("DataFrame creado con {} registros y {} columnas", len(df), len(df.columns))
                return df
            else:
                logger.warning("No se encontraron propiedades")
                return pd.DataFrame()


# Función de conveniencia para mantener compatibilidad con código existente
async def get_all_properties_acrecer_by_city(cities: List[str] = CIUDADES) -> pd.DataFrame:
    """Consulta el servicio MLS Acrecer por ciudad y devuelve un DataFrame.

    Esta es una función wrapper para mantener compatibilidad con el código existente.

    Parameters
    ----------
    cities : List[str]
        Lista de ciudades a consultar (por defecto `CIUDADES`).

    Returns
    -------
    pd.DataFrame
        DataFrame con todas las propiedades encontradas.
    """
    client = AcrecerClient()
    return await client.get_all_properties_by_cities(cities=cities)


# Para usar de forma sincrónica (si es necesario)
def get_all_properties_acrecer_by_city_sync(cities: List[str] = CIUDADES) -> pd.DataFrame:
    """Versión sincrónica de get_all_properties_acrecer_by_city.

    Parameters
    ----------
    cities : List[str]
        Lista de ciudades a consultar.

    Returns
    -------
    pd.DataFrame
        DataFrame con todas las propiedades encontradas.
    """
    return asyncio.run(get_all_properties_acrecer_by_city(cities=cities))
