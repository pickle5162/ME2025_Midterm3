import sqlite3
import os

# 定義資料庫檔案的絕對路徑，確保無論在哪裡執行都能找到它
# __file__ 變數指向當前腳本的路徑 (core/database/database.py)
# os.path.dirname(__file__) 是 core/database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, 'test_order_management.db')

class Database:
    def __init__(self, db_name=DEFAULT_DB_PATH):
        # 這裡使用完整的路徑來初始化資料庫
        self.db_path = db_name
        self.init_db()

    def init_db(self):
        """初始化資料庫並建立表格（包含 Products 和 Order_list）"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            # 建立 Products 表格
            cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                price REAL NOT NULL
            );
            """)

            # 建立 Order_list 表格
            cur.execute("""
            CREATE TABLE IF NOT EXISTS order_list (
                order_id TEXT PRIMARY KEY,
                product_date TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                product_name TEXT NOT NULL,
                product_amount INTEGER NOT NULL,
                product_total REAL NOT NULL,
                product_status TEXT NOT NULL,
                product_note TEXT,
                FOREIGN KEY (product_name) REFERENCES products(product_name)
            );
            """)

            # 插入測試數據 (用於 test/database.py)
            initial_products = [
                ('咖哩飯', '主食', 90.0),
                ('蛋包飯', '主食', 110.0),
                ('牛肉麵', '主食', 130.0),
                ('鮮奶茶', '飲料', 50.0),
                ('黑咖啡', '飲料', 45.0),
            ]
            for name, category, price in initial_products:
                try:
                    cur.execute("INSERT INTO products (product_name, category, price) VALUES (?, ?, ?)", 
                                (name, category, price))
                except sqlite3.IntegrityError:
                    pass # 避免重複插入

            # 插入測試訂單數據 (用於 test_delete_order)
            cur.execute("DELETE FROM order_list WHERE order_id = 'ORD-001'")
            cur.execute("""
            INSERT INTO order_list (order_id, product_date, customer_name, product_name, product_amount, product_total, product_status, product_note) 
            VALUES ('ORD-001', '2023-01-01', 'Initial', '咖哩飯', 1, 90.0, 'Pending', 'Initial note')
            """)
            
            conn.commit()

        except sqlite3.Error as e:
            print(f"Database Error: {e}")
        finally:
            if conn:
                conn.close()

    # 以下函式簽名修正為接受測試腳本預期的參數 (Fix 1: TypeError)
    def get_product_names_by_category(self, category):
        """根據種類取得商品名稱"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT product_name FROM products WHERE category = ?", (category,))
        results = cur.fetchall()
        conn.close()
        return results

    def get_product_price(self, product):
        """取得商品價格"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT price FROM products WHERE product_name = ?", (product,))
        result = cur.fetchone()
        conn.close()
        return result[0] if result else None

    def generate_order_id(self):
        """生成訂單 ID（簡單模擬）"""
        return 'ORD-' + str(os.urandom(4).hex()) # 用隨機字串，避免測試時衝突

    def add_order(self, order_data):
        """新增訂單"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        order_id = self.generate_order_id()
        
        try:
            cur.execute("""
                INSERT INTO order_list (order_id, product_date, customer_name, product_name, product_amount, product_total, product_status, product_note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order_id,
                order_data['product_date'],
                order_data['customer_name'],
                order_data['product_name'],
                order_data['product_amount'],
                order_data['product_total'],
                order_data['product_status'],
                order_data['product_note'],
            ))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding order: {e}")
            return False
        finally:
            conn.close()

    def get_all_orders(self):
        """取得所有訂單 (用於測試)"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        # 這裡假設會 JOIN products 表格以回傳單價 (price)
        cur.execute("""
            SELECT 
                ol.order_id, ol.product_date, ol.customer_name, ol.product_name, p.price,
                ol.product_amount, ol.product_total, ol.product_status, ol.product_note
            FROM order_list ol
            JOIN products p ON ol.product_name = p.product_name
            ORDER BY ol.product_date DESC
        """)
        results = cur.fetchall()
        conn.close()
        return results

    def delete_order(self, order_id):
        """刪除訂單"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM order_list WHERE order_id = ?", (order_id,))
            conn.commit()
            return cur.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting order: {e}")
            return False
        finally:
            conn.close()

if __name__ == '__main__':
    # 創建一個實際的資料庫檔案，供測試使用
    db = Database(DEFAULT_DB_PATH)
    print(f"資料庫初始化完成於: {DEFAULT_DB_PATH}")