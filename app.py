from flask import Flask, render_template, request, jsonify, redirect, url_for
from core.database.database import Database
import sqlite3

app = Flask(__name__)
db = Database()

def db_operation(func, *args, commit=False):
    conn = None
    try:
        conn = sqlite3.connect(db.db_path)
        cur = conn.cursor()
        result = func(cur, *args)
        if commit:
            conn.commit()
        return result
    except sqlite3.Error as e:
        raise Exception(f"Database Error: {e}")
    finally:
        if conn:
            conn.close()

@app.route('/', methods=['GET'])
def index():
    try:
        orders = db_operation(db.get_all_orders)
        categories_data = db_operation(lambda cur: cur.execute("SELECT DISTINCT category FROM commodity").fetchall())
        categories = [c[0] for c in categories_data]
        
        warning = request.args.get('warning')
        
        return render_template('form.html', orders=orders, warning=warning, categories=categories)

    except Exception as e:
        print(f"資料庫讀取失敗：{e}")
        return f"資料庫讀取失敗：{e}", 500
    
@app.route('/product', methods=['GET', 'POST', 'DELETE'])
def product():
    if request.method == 'GET':
        category = request.args.get('category')
        if category:
            try:
                products = db_operation(db.get_product_names_by_category, category)
                products_list = [{"product": p[0]} for p in products]
                return jsonify(products_list)
            except Exception as e:
                print(f"Error fetching products by category: {e}")
                return jsonify([])

        product_name = request.args.get('product')
        if product_name:
            try:
                price = db_operation(db.get_product_price, product_name)
                return jsonify({"price": price if price is not None else 0})
            except Exception as e:
                print(f"Error fetching product price: {e}")
                return jsonify({"price": 0})

        return jsonify({"message": "Missing category or product parameter"}), 400
    elif request.method == 'POST':
        order_data = request.get_json()
        required_keys = ['product_date', 'customer_name', 'product_name', 
                         'product_amount', 'product_total', 'product_status', 'product_note']
        if not all(key in order_data for key in required_keys):
            return jsonify({"error": "Missing required fields"}), 400

        try:
            db_operation(db.add_order, order_data, commit=True)
            return jsonify({"warning": "Order placed successfully"}), 200

        except Exception as e:
            print(f"Error adding order: {e}")
            return jsonify({"error": f"Database error: {e}"}), 500
    elif request.method == 'DELETE':
        order_id = request.args.get('order_id')
        if not order_id:
            return jsonify({"error": "Missing order_id"}), 400

        try:
            deleted_count = db_operation(db.delete_order, order_id, commit=True)
            
            if deleted_count:
                return jsonify({"message": "Order deleted successfully"}), 200
            else:
                return jsonify({"error": "Order ID not found"}), 404

        except Exception as e:
            print(f"Error deleting order: {e}")
            return jsonify({"error": f"Database error: {e}"}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5500, debug=True)
