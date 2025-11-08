import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_regional_coordination_offices(simplified=False):
    """Download FUNAI Regional Coordination Offices data.
    
    This function downloads and processes data for FUNAI's Regional Coordination Offices
    (Coordenações Regionais - CR), which represent the administrative offices responsible
    for managing Indigenous affairs across Brazil.
    Original source: FUNAI - Fundação Nacional dos Povos Indígenas
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with Regional Coordination Offices data
        Columns include:
        - geometry: Office location (Point)
        - undadm_sigla: Office abbreviation
        - undadm_nome: Office name
        - undadm_situacao: Office operational status
        - undadm_email: Contact email
        - undadm_uf_sigla: State abbreviation
        - mun_nome: Municipality name
        - undadm_numero_telefone: Contact phone number
        
    Example
    -------
    >>> from tunned_geobr import read_regional_coordination_offices
    >>> regional_offices = read_regional_coordination_offices()
    """
    
    url = (
        "https://geoserver.funai.gov.br/geoserver/Funai/ows"
        "?service=WFS&version=1.0.0&request=GetFeature"
        "&typeName=Funai:tis_cr&outputFormat=SHAPE-ZIP"
    )
    
    try:
        # Download the zip file with a 60-second timeout
        response = requests.get(url, timeout=60)
        if response.status_code != 200:
            raise Exception(
                f"Failed to download data from FUNAI. Status code: {response.status_code}"
            )
            
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the zip file
            with ZipFile(BytesIO(response.content)) as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the shapefile
            shp_files = [f for f in os.listdir(temp_dir) if f.endswith('.shp')]
            if not shp_files:
                raise Exception("No shapefile found in the downloaded data")
                
            # Read the shapefile
            gdf = gpd.read_file(os.path.join(temp_dir, shp_files[0]))
            gdf = gdf.to_crs(4674)  # Convert to SIRGAS 2000
            
            if simplified:
                columns_to_keep = [
                    'geometry',
                    'undadm_codigo',
                    'undadm_sigla',
                    'undadm_nome',
                    'undadm_situacao',
                    'undadm_logradouro',
                    'undadm_email',
                    'undadm_uf_sigla',
                    'mun_nome',
                    'mun_uf_sigla',
                    'undadm_numero_telefone',
                ]
                existing_columns = ['geometry'] + [
                    col for col in columns_to_keep[1:] if col in gdf.columns
                ]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading FUNAI Regional Coordination Offices data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    read_regional_coordination_offices()
