import pandas as pd

for chunk in pd.read_csv("file_name", chunksize=1000):
    chunk = chunk.dropna(['order_id'])
    chunk['order_purchase_timestamp'] = pd.to_datetime(chunk['order_purchase_timestamp'], errors = 'coerce')


import logging
from pathlib import Path

logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(levelname)s - %(message)s')
def validate_input_file(file_path:Path) -> Path:
    if not file_path.exists():
        logging.error(f" Input file {file_path} does not exist.")
        raise FileNotFoundError(f" Input file {file_path} does not exist.")
    
    logging.info(f"Input file {file_path}  exists.")
    return file_path


files = ['orders.csv','customers.csv']

column_mapping = {
    'order_id':'string',
    'customer_id': 'string',
    'order_date': 'datetime'
}

def validation(df :pd.DataFrame) -> dict:
    checks = {}
    checks['order_id_not_null'] = df['order_id'].notnull().all()
    checks['order_id_unique'] = df['order_id'].is_unique
    checks['price_non_negative'] = (df['price'] >=0).all()
    return checks



df = pd.read_csv("customers.csv")
missing_orders = df['order_id'].isna().sum()
len_before = len(df)
df = df.drop_duplicates(subset = ['order_id'])
len_after = len(df)

required_columns = ['order_id','customer_id','order_date']
missing_columns = required_columns - df.columns.tolist()
if missing_columns:
    raise ValueError

df['order_date'] = pd.to_datetime(df['order_date'], errors = 'coerce')
invalid_dates = df['order_date'].isna().sum()


logging.basicConfig(level = logging.INFO)
def extract(file_path:Path) -> pd.DataFrame:
    logging.info(f"extracting data from {file_path}")
    return pd.read_csv(file_path)

def transfrom(df:pd.DataFrame) -> pd.DataFrame:
    logging.info(f'transforming data with {len(df)} rows')
    df =df.drop_duplicates()
    df['order_date'] = pd.to_datetime(df['order_date'], errors = 'coerce')
    return df

def validate(df: pd.DataFrame) -> None:
    logging.info(f"validation data with {len(df)} rows")
    if df['order_id'].isna().any():
        raise ValueError('order_id contains null values')
    if not df['order_id'].is_unique:
        raise ValueError('order_id contains duplications')
    
def load(df:pd.DataFrame,output_path:Path) -> None:
    logging.info(f'loading data with {len(df)} rows')
    df.to_csv(output_path, index=False)

def run_pipeline(input_path:Path) ->None:
    df = extract(input_path)
    df = transfrom(df)
    validate(df)
    load(df)

if __name__ == "__main__":
    run_pipeline()

for chunk in pd.read_csv('orders.csv', chunksize=1000):
    chunk.dropna(subset=['order_id'], inplace=True)
    chunk['order_date']= pd.to_datetime(chunk['order_date'], errors='coerce')

valid_records = df[df['order_id'].notnull()]
bad_records = df[df['order_id'].isnull()]
bad_records.to_csv('bad_records.csv',index = False)











"""
select order_id, COUNT(*) as order_count
from orders
group by order_id
having COUNT(*) >1;

select * from orders  as o inner join ()
select customer_id,MAX(order_purchase_timestamp) as max_order_date
from orders
group by customer_id) as lo
on o.customer_id = lo.customer_id and o.order_purchase_timestamp = lo.order_purchase_timestamp;

select order_id,date_format(order_date,'%Y-%m') as order_month, SUM(revenue) as Total_revenue
from orders 
group by order_id,date_format(order_date,'%Y-%m')
order by order_month asc,

select customer_id,COUNT(*) as order_count
from orders
group by customer_id
having COUNT(*)>3


with cte as (
select order_id,customer_id,order_date,row_number() over (partition by customer_id order by order_date) as order_rn from orders)
select * from cte where order_rn =1


select o.order_id left join payments p on o.order_id=p.order_id where o.order_id is null;

select 'order_raw' as table_name. count(*) as row_count deom order_raw
union all
select 'order_cleaned' as table_name, count(*) as row_count from order_cleaned


select email, count(*) as email-count from customers group by email having count(*) >1,

select o.customer_id,sum(p.payment_value) as total_revenue from orders as o inner joiin payments as p on o,order_id=p.order_id
group by o.customer_id order by total_revenue desc 

select p.product_id, sum(o.price) as revenue
from order_items as o inner join products as p on o.product_id=o.product_id
groyp by p.product_id order by revenue desc limit 5


"""