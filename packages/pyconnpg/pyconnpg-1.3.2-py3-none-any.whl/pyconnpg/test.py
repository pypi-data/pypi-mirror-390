from connection import Connect


db = Connect(schema='public', table='test')

db.cursor.execute(
    """
    select * from public.test
    """
)
data = db.cursor.fetchall()
print(data)

