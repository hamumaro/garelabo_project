// calculateTotal.js の内容

document.addEventListener('DOMContentLoaded', function() {
    
    function calculateTotal() {
        let total = 0;
        
        // data-price 属性を持つすべての要素を取得
        const priceElements = document.querySelectorAll('.item-price[data-price]');

        priceElements.forEach(element => {
            // data-price の値を取得
            const priceString = element.getAttribute('data-price');
            
            // 文字列を整数に変換
            const price = parseInt(priceString, 10);
            
            // 有効な数値であれば合計に加算
            if (!isNaN(price)) {
                total += price;
            }
        });
        
        return total;
    }

    function updateTotalPrice() {
        const total = calculateTotal();
        const totalDisplayElement = document.getElementById('totalAmont');
        
        if (totalDisplayElement) {
            // 金額をカンマ区切りで整形し、表示を更新
            const formattedTotal = total.toLocaleString('ja-JP');
            
            // JPY〜 を付加して表示
            totalDisplayElement.textContent = `${formattedTotal} JPY〜`;
        }
    }

    // ページ読み込み完了時に実行
    updateTotalPrice();
});