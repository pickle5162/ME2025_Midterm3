// 開啟與關閉Modal
function open_input_table() {
    document.getElementById("addModal").style.display = "block";
}
function close_input_table() {
    document.getElementById("addModal").style.display = "none";
}

function delete_data(value) {
    // 發送 DELETE 請求到後端
    fetch(`/product?order_id=${value}`, {
        method: "DELETE",
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("伺服器回傳錯誤");
        }
        return response.json(); // 假設後端回傳 JSON 格式資料
    })
    .then(result => {
        console.log(result); // 在這裡處理成功的回應
        close_input_table(); // 關閉 modal
        location.assign('/'); // 重新載入頁面
    })
    .catch(error => {
        console.error("發生錯誤：", error);
    });
}
function getInputValue(id, isNumeric = false) {
    const element = document.getElementById(id);
    if (!element) return isNumeric ? 0 : '';
    const value = element.value;
    return isNumeric ? (parseFloat(value) || 0) : value;
}

function setInputValue(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.value = value;
    }
}
function open_input_table() {
    document.getElementById("addModal").style.display = "block";
    initializeForm(); 
}
function close_input_table() {
    document.getElementById("addModal").style.display = "none";
}

function delete_data(value) {
    fetch(`/product?order_id=${value}`, {
        method: "DELETE",
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.error || "伺服器回傳錯誤"); });
        }
        return response.json(); 
    })
    .then(result => {
        console.log(result); 
        close_input_table(); 
        location.assign('/');
    })
    .catch(error => {
        console.error("發生錯誤：", error);
        alert(`刪除失敗: ${error.message}`);
    });
}
function countTotal() {
    const price = getInputValue('product_price', true);
    let amount = getInputValue('product_amount', true);
    if (amount <= 0) {
        amount = 1;
        setInputValue('product_amount', 1);
    }
    if (isNaN(amount)) {
        amount = 1;
        setInputValue('product_amount', 1);
    }
    const total = price * amount;
    setInputValue('product_total', total.toFixed(0));
}
async function selectCategory() {
    const category = getInputValue('category');
    const productSelect = document.getElementById('product_name');
    productSelect.innerHTML = '<option value="">請選擇商品名稱</option>';
    setInputValue('product_price', 0);
    countTotal(); 

    if (!category) {
        return;
    }

    try {
        const response = await fetch(`/product?category=${encodeURIComponent(category)}`);
        if (!response.ok) {
            throw new Error(`伺服器回傳錯誤: ${response.status}`);
        }
        const products = await response.json(); 
        products.forEach(item => {
            const option = document.createElement('option');
            option.value = item.product; 
            option.textContent = item.product;
            productSelect.appendChild(option);
        });

    } catch (error) {
        console.error("取得商品列表失敗：", error);
    }
}
async function selectProduct() {
    const product = getInputValue('product_name');
    setInputValue('product_price', 0);
    countTotal();

    if (!product) {
        return;
    }

    try {
        const response = await fetch(`/product?product=${encodeURIComponent(product)}`);
        if (!response.ok) {
            throw new Error(`伺服器回傳錯誤: ${response.status}`);
        }
        const result = await response.json(); 
        const price = result.price || 0;
        setInputValue('product_price', price);
        countTotal();

    } catch (error) {
        console.error("取得商品價格失敗：", error);
    }
}
async function submitOrder() {
    const orderData = {
        product_date: getInputValue('product_date'), 
        customer_name: getInputValue('customer_name'),
        product_name: getInputValue('product_name'),
        product_amount: getInputValue('product_amount', true),
        product_total: getInputValue('product_total', true), 
        product_status: getInputValue('product_status'), 
        product_note: getInputValue('product_note') 
    };
    if (!orderData.customer_name || !orderData.product_name || orderData.product_amount <= 0) {
        alert("請檢查：客戶名稱、商品名稱為必填，且數量必須大於零。");
        return;
    }

    try {
        const response = await fetch('/product', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
        });
        if (response.status === 200) {
            close_input_table(); 
            location.assign('/?warning=Order placed successfully'); 
        } else {
            const result = await response.json();
            alert(`訂單新增失敗: ${result.warning || result.error || '未知錯誤'}`);
        }
    } catch (error) {
        console.error("發送訂單失敗：", error);
        alert("網路錯誤或伺服器無回應，無法送出訂單。");
    }
}

function initializeForm() {
    const today = new Date().toISOString().split('T')[0];
    setInputValue('product_date', today);
    setInputValue('product_amount', 1);
    setInputValue('product_status', '未付款');
    setInputValue('product_price', 0);
    setInputValue('product_total', 0);
    countTotal(); 
}
document.addEventListener('DOMContentLoaded', () => {
    const priceInput = document.getElementById('product_price');
    const amountInputCalc = document.getElementById('product_amount');
    if (priceInput) priceInput.addEventListener('input', countTotal);
    if (amountInputCalc) amountInputCalc.addEventListener('input', countTotal); 
    const categorySelect = document.getElementById('category');
    const productSelect = document.getElementById('product_name');
    if (categorySelect) categorySelect.addEventListener('change', selectCategory);
    if (productSelect) productSelect.addEventListener('change', selectProduct);
    initializeForm(); 
});