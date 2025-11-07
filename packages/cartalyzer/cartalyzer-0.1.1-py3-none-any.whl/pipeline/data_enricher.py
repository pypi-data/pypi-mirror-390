import pandas as pd
import duckdb


from pandas import DataFrame



class DataEnricher:
    """Combine and clean data from two sources into one dataframe"""
    
    def enrich_data(self, products, users) -> DataFrame:
        
        df_products = pd.DataFrame(products)
        df_users = pd.DataFrame(users)
        # print(df_users)
        
        query = """SELECT 
                    COALESCE(u.name, 'Unknown user') AS name, 
                    COALESCE(u.email, 'Unknown user') AS email, 
                    COALESCE(u.username, 'Unknown user') AS username, 
                    p.*,
                    CAST(json_extract(rating, '$.count') AS DECIMAL(10,2)) * p.price AS revenue
                    FROM df_products p
                    LEFT JOIN df_users u ON p.id = u.id"""
        
        df_combined = duckdb.query(query).df()
        return df_combined
        
        
        
