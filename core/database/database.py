import datetime
import os
import random

class Database():
    def __init__(self, db_filename="order_management.db"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, db_filename)

    @staticmethod
    def generate_order_id() -> str:
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        random_num = random.randint(1000, 9999)
        return f"OD{timestamp}{random_num}"

    def get_product_names_by_category(self, cur, category):
        query = "SELECT product FROM commodity WHERE category = ?"
        cur.execute(query, (category,))
        return cur.fetchall()

    def get_product_price(self, cur, product):
        query = "SELECT price FROM commodity WHERE product = ?"
        cur.execute(query, (product,))
        result = cur.fetchone()
        return result[0] if result else None
    
    def add_order(self, cur, order_data):
        """
        將訂單資料字典寫入 order_list。
        修正: 欄位名稱從 product_date/customer_name/product_name -> date/customer_name/product
        """
        order_id = Database.generate_order_id()
        
        columns = ('order_id', 'date', 'customer_name', 'product', 
                   'amount', 'total', 'status', 'note')

        params = (order_id, 
                  order_data.get('product_date'), 
                  order_data.get('customer_name'), 
                  order_data.get('product_name'), 
                  order_data.get('product_amount'), 
                  order_data.get('product_total'), 
                  order_data.get('product_status'), 
                  order_data.get('product_note'))
        
        query = f"""
            INSERT INTO order_list ({', '.join(columns)}) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cur.execute(query, params)
        return True
    
    def get_all_orders(self, cur):
        """
        取得所有訂單，並合併商品價格。
        重點修正：調整 SELECT 欄位順序以匹配前端表格標題 (單價, 數量, 小計, 狀態, 備註)。
        """
        query = """
            SELECT 
                o.order_id, 
                o.date, 
                o.customer_name, 
                o.product, 
                
                c.price,        -- 調整到這裡：對應前端的「單價」
                o.amount,       -- 調整到這裡：對應前端的「數量」
                o.total,        -- 調整到這裡：對應前端的「小計」
                o.status,       -- 調整到這裡：對應前端的「狀態」
                o.note          -- 調整到這裡：對應前端的「備注」
                
            FROM 
                order_list o
            JOIN 
                commodity c ON o.product = c.product 
            ORDER BY 
                o.date DESC
        """
        cur.execute(query)
        return cur.fetchall()
    
    def delete_order(self, cur, order_id):
        query = "DELETE FROM order_list WHERE order_id = ?"
        cur.execute(query, (order_id,))
        return cur.rowcount > 0 