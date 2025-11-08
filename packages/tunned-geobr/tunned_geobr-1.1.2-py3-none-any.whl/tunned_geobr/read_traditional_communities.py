import geopandas as gpd
import requests


def read_traditional_communities(layer="territorios_pontos", timeout=60):
    """Download Traditional Communities data from the Public Ministry's API."""

    url = f"https://territoriostradicionais.mpf.mp.br/api/camada/{layer}/?format=json"

    try:
        features = []
        next_url = url

        while next_url:
            resp = requests.get(next_url, timeout=timeout)
            resp.raise_for_status()

            data = resp.json()
            if not isinstance(data, dict) or data.get("type") != "FeatureCollection":
                raise ValueError("Unexpected response format from MPF API")

            features.extend(data.get("features", []))
            next_url = data.get("next")  # may be None if pagination ends

        if not features:
            raise ValueError("No features returned by MPF API")

        gdf = gpd.GeoDataFrame.from_features(features, crs="EPSG:4326")

        if gdf.crs is None or gdf.crs.to_epsg() != 4674:
            gdf = gdf.to_crs(4674)

        return gdf

    except Exception as e:
        raise RuntimeError(f"Error downloading Traditional Communities data: {e}")
