// list.js (仮のファイル名)

const CUSTOM_API_URL = 'http://localhost:8000/api/customs/'; // ★ DjangoのURLに合わせる
const customListContainer = document.querySelector('.custom-list');

// 仮の認証トークン（実際はログイン後に取得したJWTトークンを使用）
const MOCK_AUTH_TOKEN = 'YOUR_JWT_TOKEN_HERE'; 

// バックエンドからデータを取得し、HTMLを生成する関数
async function fetchAndRenderCustoms() {
    try {
        const response = await fetch(CUSTOM_API_URL, {
            method: 'GET',
            headers: {
                // 認証トークンをヘッダーに含める (Spring SecurityのIsAuthenticatedに対応)
                'Authorization': `Bearer ${MOCK_AUTH_TOKEN}`, 
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            // エラー処理（例：未認証、サーバーエラーなど）
            console.error('Failed to fetch customs:', response.statusText);
            customListContainer.innerHTML = '<p>カスタムデータを取得できませんでした。ログイン状態を確認してください。</p>';
            return;
        }

        const data = await response.json();
        
        // 取得したデータをもとにリストを生成
        renderCustomList(data);

    } catch (error) {
        console.error('Error during API call:', error);
        customListContainer.innerHTML = '<p>ネットワークエラーが発生しました。</p>';
    }
}

// 取得したデータ配列をHTMLに変換する関数
function renderCustomList(customs) {
    if (customs.length === 0) {
        customListContainer.innerHTML = '<p>保存されたカスタム設定はありません。</p>';
        return;
    }
    
    const htmlItems = customs.map(custom => {
        // 日付のフォーマットを整形
        const savedDate = new Date(custom.saved_at).toLocaleDateString('ja-JP', {
            year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'
        });
        
        // 価格をカンマ区切りに整形 (例: 2500000.00 -> 2,500,000)
        const totalPrice = Number(custom.total_price).toLocaleString('ja-JP');

        // お気に入りアイコンを決定
        const favoriteIcon = custom.is_favorite ? '★' : '☆';
        const favoriteClass = custom.is_favorite ? 'active' : '';

        // リストアイテムのHTML構造をテンプレートリテラルで記述
        return `
            <div class="custom-item" data-custom-id="${custom.id}">
                <div class="item-footer">
                    <p class="saved-date">最終保存日: ${savedDate}</p>
                </div>
                
                <button class="delete-btn" data-custom-id="${custom.id}">削除</button>
            </div>
        `;
    }).join('');

    customListContainer.innerHTML = htmlItems;
    
    // ★ 削除ボタンにイベントリスナーを設定
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            const customId = e.target.getAttribute('data-custom-id');
            // 削除処理を開始
            deleteCustom(customId, e.target.closest('.custom-item'));
        });
    });
}

// ★ 削除処理を実行する関数を定義
async function deleteCustom(customId, itemElement) {
    if (!confirm(`カスタムID ${customId} を本当に削除しますか？`)) {
        return; // キャンセルされたら何もしない
    }

    const DELETE_API_URL = `http://localhost:8000/api/customs/${customId}/`; // ★ バックエンドのDELETEエンドポイント

    try {
        const response = await fetch(DELETE_API_URL, {
            method: 'DELETE', // HTTP DELETE メソッドを使用
            headers: {
                'Authorization': `Bearer ${MOCK_AUTH_TOKEN}`,
            }
        });

        if (response.ok || response.status === 204) { // 204 No Content も成功
            alert('カスタム設定を削除しました。');
            // 成功したら、リストから該当のHTML要素を削除
            itemElement.remove();
        } else {
            alert('削除に失敗しました。認証トークンやサーバー設定を確認してください。');
        }
    } catch (error) {
        console.error('Error during DELETE API call:', error);
        alert('ネットワークエラーにより削除できませんでした。');
    }
}

// ページロード時に実行
document.addEventListener('DOMContentLoaded', fetchAndRenderCustoms);