"""
現場報告DXシステム - UIコンポーネント
PC版とスマホ版のUI構築モジュール
"""
from nicegui import ui

def create_shared_ui_elements():
    """PC/スマホ共通のUI要素"""
    pass

def create_mobile_ui(handle_upload, update_user_info, tags, location_presets):
    """スマホ向けの最小UI構築

    Args:
        handle_upload: アップロード処理関数
        update_user_info: ユーザー情報更新関数
        tags: 選択可能なタグリスト
        location_presets: 場所のプリセットリスト
    """
    with ui.card().classes("w-full"):
        ui.label("現場からの報告").classes("text-lg font-bold")

        # 名前入力
        name_input = ui.input(
            label="名前", placeholder="山田 太郎"
        ).classes("w-full")

        # 場所選択（プリセットからドロップダウン + 手動入力）
        location_select = ui.select(
            label="場所",
            options=location_presets,
            with_input=True
        ).classes("w-full")

        # タグ選択（複数選択可能）
        tag_select = ui.select(
            label="タグ",
            options=tags,
            multiple=True
        ).classes("w-full")

        # コメント入力
        comment_input = ui.input(
            label="コメント",
            placeholder="必要に応じてコメントを入力"
        ).classes("w-full")

        # ユーザー情報を更新するヘルパー関数
        def update_info():
            name = name_input.value or "名前未設定"
            location = location_select.value or "場所未設定"
            selected_tags = tag_select.value or []
            comment = comment_input.value or ""

            update_user_info(
                name=name,
                location=location,
                tags=selected_tags,
                comment=comment
            )

        # フォーム変更時に情報を更新
        name_input.on("change", lambda _: update_info())
        location_select.on("change", lambda _: update_info())
        tag_select.on("change", lambda _: update_info())
        comment_input.on("change", lambda _: update_info())

        # アップロードエリア（シンプルに）
        with ui.card().classes("w-full bg-blue-50 p-4 mt-4"):
            ui.label("写真をアップロード").classes("text-center font-bold mb-2")

            # アップロードボタン（わかりやすく大きく）
            upload = ui.upload(
                label="タップして写真を選択",
                multiple=True,
                on_upload=handle_upload
            ).classes("w-full")

            # カメラアクセス（モバイル用）
            with ui.card().classes("mt-4 bg-green-50 p-2"):
                ui.label("または直接撮影").classes("text-center mb-2")

                camera_upload = ui.upload(
                    label="カメラで撮影",
                    multiple=True,
                    on_upload=handle_upload,
                    auto_upload=True
                ).props('accept="image/*" capture="environment"').classes("w-full")

                ui.label("※カメラアイコンをタップすると撮影できます").classes("text-xs text-center mt-2")

def create_desktop_ui(handle_upload, update_user_info, send_to_slack, save_as_zip, tags, location_presets):
    """PC向けの管理者UI構築

    Args:
        handle_upload: アップロード処理関数
        update_user_info: ユーザー情報更新関数
        send_to_slack: Slack送信関数
        save_as_zip: ZIP保存関数
        tags: 選択可能なタグリスト
        location_presets: 場所のプリセットリスト
    """
    # 2カラムレイアウト
    with ui.row().classes("w-full gap-4"):
        # 左カラム：フォーム入力
        with ui.column().classes("w-1/3"):
            with ui.card().classes("w-full sticky top-4"):
                ui.label("報告情報入力").classes("text-lg font-bold")

                # 名前入力
                name_input = ui.input(
                    label="名前", placeholder="管理者 / 職人名"
                ).classes("w-full")

                # 場所選択
                location_select = ui.select(
                    label="場所",
                    options=location_presets,
                    with_input=True
                ).classes("w-full")

                # タグ選択（複数選択可能）
                tag_select = ui.select(
                    label="タグ",
                    options=tags,
                    multiple=True
                ).classes("w-full")

                # コメント入力
                comment_input = ui.textarea(
                    label="コメント",
                    placeholder="必要に応じてコメントを入力"
                ).classes("w-full")

                # ユーザー情報を更新するヘルパー関数
                def update_info():
                    name = name_input.value or "名前未設定"
                    location = location_select.value or "場所未設定"
                    selected_tags = tag_select.value or []
                    comment = comment_input.value or ""

                    update_user_info(
                        name=name,
                        location=location,
                        tags=selected_tags,
                        comment=comment
                    )

                # フォーム変更時に情報を更新
                name_input.on("change", lambda _: update_info())
                location_select.on("change", lambda _: update_info())
                tag_select.on("change", lambda _: update_info())
                comment_input.on("change", lambda _: update_info())

        # 右カラム：アップロードと管理
        with ui.column().classes("w-2/3"):
            # アップロードエリア
            with ui.card().classes("w-full mb-4"):
                ui.label("写真をアップロード").classes("text-lg font-bold")

                # アップロードコンポーネント
                upload = ui.upload(
                    label="ファイルをドラッグまたはクリックして選択",
                    multiple=True,
                    on_upload=handle_upload
                ).classes("w-full")

                # 注意書き
                ui.label("※一度に複数の画像をアップロードできます").classes("text-xs text-gray-500 mt-2")

            # 管理者向け機能ボタン
            with ui.card().classes("w-full mb-4 p-4 bg-gray-50"):
                ui.label("管理者機能").classes("text-lg font-bold")

                with ui.row().classes("gap-2 justify-center"):
                    ui.button(
                        "Slackに送信",
                        color="green",
                        icon="send",
                        on_click=send_to_slack
                    ).classes("m-2")

                    ui.button(
                        "ZIPで保存",
                        color="blue",
                        icon="archive",
                        on_click=save_as_zip
                    ).classes("m-2")

                    ui.button(
                        "すべて削除",
                        color="red",
                        icon="delete",
                        on_click=lambda: ui.notify("この機能は未実装です", color="warning")
                    ).classes("m-2")