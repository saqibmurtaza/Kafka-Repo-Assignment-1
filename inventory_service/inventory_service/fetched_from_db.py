from .database import supabase 
import json, logging

# EXTRACT DATA FROM DB TABLE CATALOGUE OF PRODUCT SERVICE 

def fetch_data(id:int):
    response= supabase.from_('catalogue').select('*').eq('id', id).execute()
    logging.info(f"EXTRACTED CATALOGUE FROM DB:{response}")
    
    response_dict= response.json()
    if isinstance(response_dict, str):
        response_dict= json.loads(response_dict)

    for my_data in response_dict.get('data', []):
        if my_data['id'] == id:
            fetched_product= my_data
        return fetched_product
    None