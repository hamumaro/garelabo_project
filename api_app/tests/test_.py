from api_app.models import Vehicle, Wheel, Color, Bumper

def register_full_data():
    # ==========================================
    # ★設定エリア
    # ==========================================
    CAR_NAME_JP = "ロッキー"      # 日本語名
    CAR_NAME_EN = "Rocky"         # 英名フォルダ用
    BASE_PATH = "uploads/vehicles"

    # カラー設定
    COLOR_LIST = [
        ("白", "white"),
        ("黒", "black"),
    ]

    # ホイール設定
    WHEEL_LIST = [
        ("ホイール1", "wheel1"),
        ("ホイール2", "wheel2"),
    ]

    # バンパー設定
    BUMPER_LIST = [
        ("標準バンパー", "bumper1"),
        # 必要なら追加: ("エアロバンパー", "bumper2"),
    ]

    print(f"=== {CAR_NAME_JP} ({CAR_NAME_EN}) のデータ登録を開始します ===")

    # --------------------------------------------------
    # 1. 車両データの取得・作成
    # --------------------------------------------------
    # base.png のパス生成 (例: uploads/vehicles/Rocky/white/base.png)
    default_base_image = f"{BASE_PATH}/{CAR_NAME_EN}/{COLOR_LIST[0][1]}"

    target_vehicle, created = Vehicle.objects.get_or_create(
        name=CAR_NAME_JP,
        defaults={
            'base_image_path': default_base_image,
            'name_en': CAR_NAME_EN
        }
    )

    if created:
        print(f"✔ 車両「{target_vehicle.name}」を新規作成しました。")
    else:
        print(f"✔ 車両「{target_vehicle.name}」を取得しました。(既存)")
        # 既存の場合も設定を上書き更新
        target_vehicle.base_image_path = default_base_image
        target_vehicle.name_en = CAR_NAME_EN
        target_vehicle.save()

    # --------------------------------------------------
    # 2. カラーの登録
    # --------------------------------------------------
    print("\n--- カラー登録 ---")
    for name, folder in COLOR_LIST:
        color_path = f"{BASE_PATH}/{CAR_NAME_EN}/{folder}"
        
        Color.objects.update_or_create(
            vehicle=target_vehicle,
            name=name,
            defaults={
                'price': 0,
                'image_url': color_path,
                'rotation_image_folder': folder
            }
        )
        print(f"  OK: {name}")

    # --------------------------------------------------
    # 3. ホイール & バンパーの登録 (階層構造)
    # --------------------------------------------------
    print("\n--- ホイール・バンパー登録 ---")

    # ループ1: 色
    for color_name, color_folder in COLOR_LIST:
        print(f"[{color_name}ボディ用]")
        
        # ループ2: ホイール
        for wheel_name, wheel_folder in WHEEL_LIST:
            # ホイールのパス: uploads/vehicles/Rocky/white/wheel1
            wheel_path = f"{BASE_PATH}/{CAR_NAME_EN}/{color_folder}/{wheel_folder}"
            wheel_full_name = f"{wheel_name} ({color_name})"
            
            Wheel.objects.update_or_create(
                vehicle=target_vehicle,
                image_url=wheel_path,
                defaults={
                    'name': wheel_full_name,
                    'price': 0
                }
            )
            print(f"  └ Wheel: {wheel_full_name}")

            # ループ3: バンパー (ホイールの下の階層)
            for bumper_name, bumper_folder in BUMPER_LIST:
                # バンパーのパス: uploads/vehicles/Rocky/white/wheel1/bumper1
                bumper_path = f"{wheel_path}/{bumper_folder}"
                bumper_full_name = f"{bumper_name} ({color_name}, {wheel_name})"
                
                Bumper.objects.update_or_create(
                    vehicle=target_vehicle,
                    image_url=bumper_path,
                    defaults={
                        'name': bumper_full_name,
                        'price': 0
                    }
                )
                print(f"      └ Bumper: {bumper_folder}")

    print("\n=== 全ての処理が完了しました ===")

# 関数を実行
register_full_data()