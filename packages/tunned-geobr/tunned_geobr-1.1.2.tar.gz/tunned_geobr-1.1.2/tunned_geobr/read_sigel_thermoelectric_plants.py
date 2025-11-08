import geopandas as gpd
import os
import tempfile
import urllib.parse
import requests
import shutil
from zipfile import ZipFile
from pathlib import Path
from io import BytesIO
import warnings
import json
import time

def read_sigel_thermoelectric_plants(simplified=False, verbose=False):
    """Download Thermoelectric Plants data from Sigel.
    
    This function downloads and processes thermoelectric plants data from Sigel (ANEEL).
    Original source: ANEEL (Agência Nacional de Energia Elétrica)
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
    verbose : boolean, by default False
        If True, prints detailed information about the download process

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with thermoelectric plants data
        
    Example
    -------
    >>> from tunned_geobr import read_sigel_thermoelectric_plants
    
    # Read thermoelectric plants data
    >>> thermoelectric_plants = read_sigel_thermoelectric_plants()
    """
    
    # URL for the Sigel geoserver WFS service
    url = r'https://sigel.aneel.gov.br/arcgis/rest/services/PORTAL/ExtractDataPro/GPServer/ExtractDataPro/submitJob?f=json&env%3AoutSR=102100&Layers_to_Clip=%5B%22Usinas%20Termel%C3%A9tricas%20-%20UTE%22%5D&Area_of_Interest=%7B%22geometryType%22%3A%22esriGeometryPolygon%22%2C%22features%22%3A%5B%7B%22geometry%22%3A%7B%22rings%22%3A%5B%5B%5B-8938378.510524046%2C-4460571.882677736%5D%2C%5B-8938378.510524046%2C1165193.3991097403%5D%2C%5B-3058230.79860357%2C1165193.3991097403%5D%2C%5B-3058230.79860357%2C-4460571.882677736%5D%2C%5B-8938378.510524046%2C-4460571.882677736%5D%5D%5D%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D%7D%5D%2C%22sr%22%3A%7B%22wkid%22%3A102100%7D%7D&Feature_Format=Shapefile%20-%20SHP%20-%20.shp&Raster_Format=ESRI%20GRID%20-%20GRID&Spatial_Reference=Same%20As%20Input'
 
    try:
        # Disable SSL verification warning
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        
        if verbose:
            print("Requesting data from Sigel server...")
            
        response = requests.get(url, timeout=60, verify=False)
        if not response.ok:
            raise Exception(f"Error getting JSON response: {response.status_code}")

        json_response = response.json()
        
        if verbose:
            print(f"JSON response received: {json.dumps(json_response, indent=2)[:500]}...")
            
        job_id = json_response.get('jobId')
        if not job_id:
            raise Exception("Job ID not found in JSON response")

        if verbose:
            print(f"Job submitted successfully with ID: {job_id}")

        job_status_url = (
            "https://sigel.aneel.gov.br/arcgis/rest/services/PORTAL/ExtractDataPro/"
            f"GPServer/ExtractDataPro/jobs/{job_id}"
        )
        max_attempts = 30
        poll_interval = 5
        final_status_json = None

        for attempt in range(1, max_attempts + 1):
            params = {
                'f': 'json',
                'dojo.preventCache': str(int(time.time() * 1000))
            }
            status_response = requests.get(job_status_url, params=params, timeout=60, verify=False)
            if not status_response.ok:
                raise Exception(f"Error checking job status: {status_response.status_code}")

            status_json = status_response.json()
            job_status = status_json.get('jobStatus')

            if verbose:
                print(f"Polling attempt {attempt}: job status = {job_status}")

            if job_status == 'esriJobSucceeded':
                final_status_json = status_json
                break

            if job_status in {'esriJobFailed', 'esriJobCancelled'}:
                error_messages = status_json.get('messages', [])
                raise Exception(f"Job ended with status {job_status}. Messages: {error_messages}")

            time.sleep(poll_interval)

        if final_status_json is None:
            raise Exception("Job did not succeed within the expected time frame")

        results_url = f"{job_status_url}/results/Output_Zip_File"
        results_params = {
            'f': 'json',
            'returnType': 'data',
            'dojo.preventCache': str(int(time.time() * 1000))
        }

        if verbose:
            print(f"Fetching job results from: {results_url}")

        results_response = requests.get(results_url, params=results_params, timeout=60, verify=False)
        if not results_response.ok:
            raise Exception(f"Error fetching job results: {results_response.status_code}")

        results_json = results_response.json()
        file_url = results_json.get('value', {}).get('url')
        if not file_url:
            raise Exception("Download URL not found in job results")

        if verbose:
            print(f"Downloading file from: {file_url}")

        file_response = requests.get(file_url, stream=True, timeout=60, verify=False)
        if not file_response.ok:
            raise Exception(f"Error downloading file: {file_response.status_code}")
        
        # Check if content is actually a zip file
        content = file_response.content
        if len(content) < 100:
            if verbose:
                print(f"Warning: Downloaded content is very small ({len(content)} bytes)")
                print(f"Content preview: {content[:100]}")
            
        # Create a temporary directory to extract the files
        with tempfile.TemporaryDirectory() as temp_dir:
            if verbose:
                print(f"Extracting files to temporary directory: {temp_dir}")
                
            try:
                # Extract the zip file
                with ZipFile(BytesIO(content)) as zip_ref:
                    zip_ref.extractall(temp_dir)
                    
                    if verbose:
                        print(f"Files in zip: {zip_ref.namelist()}")
            except Exception as zip_error:
                if verbose:
                    print(f"Error extracting zip: {str(zip_error)}")
                    print(f"Saving content to debug.zip for inspection")
                    with open("debug.zip", "wb") as f:
                        f.write(content)
                raise Exception(f"Failed to extract zip file: {str(zip_error)}")
            
            # Find the shapefile
            all_files = os.listdir(temp_dir)
            if verbose:
                print(f"Files in temp directory: {all_files}")
                
            shp_files = [f for f in all_files if f.endswith('.shp')]
            if not shp_files:
                # Try looking in subdirectories
                for root, dirs, files in os.walk(temp_dir):
                    shp_files.extend([os.path.join(root, f) for f in files if f.endswith('.shp')])
                
                if not shp_files:
                    raise Exception("No shapefile found in the downloaded data")
            
            # Read the shapefile
            shp_path = shp_files[0] if os.path.isabs(shp_files[0]) else os.path.join(temp_dir, shp_files[0])
            if verbose:
                print(f"Reading shapefile: {shp_path}")
                
            gdf = gpd.read_file(shp_path)
            
            # Convert to SIRGAS 2000 (EPSG:4674)
            gdf = gdf.to_crs(4674)
            
            if verbose:
                print(f"Data loaded successfully with {len(gdf)} records")
                print(f"Columns: {gdf.columns.tolist()}")
            
            if simplified:
                # Keep only the most relevant columns based on actual data structure
                columns_to_keep = [
                    'geometry',
                    # Add relevant columns for thermoelectric plants here
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                if len(existing_columns) <= 1:
                    if verbose:
                        print("Warning: No matching columns found for simplified version. Returning all columns.")
                else:
                    gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading or processing thermoelectric plants data: {str(e)}")
        
    return gdf
