import pandas as pd

pd.options.mode.chained_assignment = None
class DataAnalyzer:
    """Analyzes enriched data"""
    

    def analyze_data(self, enriched_data) -> dict[str, int]:
        df = enriched_data[['username', 'revenue', 'price']]
        df['quantity'] = enriched_data['rating'].apply(lambda x: x['count'])
        df_analysis = df.groupby('username').agg({'revenue': 'sum', 'price': 'mean', 'quantity': 'sum'})
        df_analysis = df_analysis.reset_index()
        final_result = {}
        for _, row in df_analysis.iterrows():
            result = {}
            result['total_revenue'] = row['revenue']
            result['total_prods_sold'] = row['quantity']
            result['average_prod_price'] = row['price']
            
            final_result[row['username']] = result
        
        return final_result
    
    