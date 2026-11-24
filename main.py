import socket
import threading
import time
import flet as ft
import requests

SOURCES = [
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/Sub1.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
]

TG_URL = "https://t.me/Ars3nbar_osn"
TT_URL = "https://www.tiktok.com/@ars3nbar"


def parse_host_port(uri: str):
    try:
        if "@" in uri:
            after_at = uri.split("@", 1)[1]
            host_port = after_at.split("?", 1)[0].split("#", 1)[0]
            if ":" in host_port:
                host, port = host_port.rsplit(":", 1)
                return host.strip("[]"), int(port)
    except Exception:
        pass
    return None, None


def check_ping(host: str, port: int, timeout: float = 1.5):
    start = time.time()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return int((time.time() - start) * 1000)
    except Exception:
        return None


def main(page: ft.Page):
    page.title = "ABvpn"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#090B10"
    page.window.width = 430
    page.window.height = 740
    page.padding = 20

    selected_uri = {"value": ""}

    shield_icon = ft.Icon(ft.Icons.SHIELD_MOON_ROUNDED, size=48, color="#38BDF8")
    shield_ring = ft.Container(
        content=shield_icon,
        width=84,
        height=84,
        border_radius=42,
        bgcolor="#111827",
        border=ft.border.all(2, "#1E293B"),
        alignment=ft.alignment.center,
        scale=ft.Scale(1.0),
        animate_scale=ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT),
        animate=ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT),
        shadow=ft.BoxShadow(blur_radius=20, color="#1D4ED833"),
    )

    header = ft.Row(
        controls=[
            ft.Column(
                controls=[
                    ft.Text("ABvpn", size=28, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
                    ft.Text("Free Global Proxy Hub", size=12, color="#94A3B8"),
                ],
                spacing=2,
            ),
            ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.TELEGRAM,
                        icon_color="#38BDF8",
                        tooltip="Telegram",
                        on_click=lambda _: page.launch_url(TG_URL),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.MUSIC_NOTE_ROUNDED,
                        icon_color="#F43F5E",
                        tooltip="TikTok",
                        on_click=lambda _: page.launch_url(TT_URL),
                    ),
                ],
                spacing=0,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    status_text = ft.Text(
        "Нажмите «Найти серверы» для сканирования",
        size=13,
        color="#94A3B8",
        text_align=ft.TextAlign.CENTER,
    )

    active_text = ft.Text("Сервер не выбран", size=13, color="#CBD5E1", weight=ft.FontWeight.W_500)
    active_box = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.DNS_ROUNDED, color="#38BDF8", size=20),
                active_text,
            ],
            spacing=10,
        ),
        padding=14,
        border_radius=14,
        bgcolor="#111827",
        border=ft.border.all(1, "#1E293B"),
        animate=ft.Animation(350, ft.AnimationCurve.EASE_OUT),
    )

    def copy_uri(e):
        if selected_uri["value"]:
            page.set_clipboard(selected_uri["value"])
            status_text.value = "Ключ скопирован в буфер обмена!"
            status_text.color = "#34D399"
            shield_ring.scale = ft.Scale(1.12)
            shield_ring.border = ft.border.all(2, "#10B981")
            shield_icon.color = "#34D399"
            page.update()
            time.sleep(0.35)
            shield_ring.scale = ft.Scale(1.0)
            page.update()

    connect_btn = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.CONTENT_COPY_ROUNDED, color="#090B10", size=20),
                ft.Text("Скопировать ключ", size=15, weight=ft.FontWeight.BOLD, color="#090B10"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        height=48,
        border_radius=14,
        gradient=ft.LinearGradient(
            begin=ft.alignment.center_left,
            end=ft.alignment.center_right,
            colors=["#38BDF8", "#818CF8"],
        ),
        opacity=0.4,
        disabled=True,
        on_click=copy_uri,
        animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )

    servers_list = ft.ListView(expand=True, spacing=10)

    def select_server(uri: str, label: str):
        selected_uri["value"] = uri
        active_text.value = label
        active_box.border = ft.border.all(1, "#38BDF8")
        connect_btn.disabled = False
        connect_btn.opacity = 1.0
        shield_ring.border = ft.border.all(2, "#38BDF8")
        shield_icon.color = "#38BDF8"
        page.update()

    def fetch_and_test(e):
        scan_btn.disabled = True
        scan_btn.opacity = 0.6
        servers_list.controls.clear()
        status_text.value = "Сканируем открытые узлы и замеряем пинг..."
        status_text.color = "#FBBF24"
        shield_ring.scale = ft.Scale(1.08)
        shield_ring.border = ft.border.all(2, "#FBBF24")
        shield_icon.color = "#FBBF24"
        page.update()

        def worker():
            raw_uris = []
            for url in SOURCES:
                try:
                    resp = requests.get(url, timeout=8)
                    if resp.status_code == 200:
                        for line in resp.text.splitlines():
                            line = line.strip()
                            if line.startswith(("vless://", "trojan://", "ss://")):
                                raw_uris.append(line)
                except Exception:
                    continue

            checked = []
            for uri in raw_uris[:75]:
                host, port = parse_host_port(uri)
                if host and port:
                    ping = check_ping(host, port)
                    if ping is not None:
                        proto = uri.split("://", 1)[0].upper()
                        checked.append((ping, proto, host, port, uri))
                if len(checked) >= 15:
                    break

            checked.sort(key=lambda x: x[0])

            servers_list.controls.clear()
            shield_ring.scale = ft.Scale(1.0)
            if not checked:
                status_text.value = "Рабочие узлы не найдены. Попробуйте снова."
                status_text.color = "#F87171"
                shield_ring.border = ft.border.all(2, "#F87171")
                shield_icon.color = "#F87171"
            else:
                status_text.value = f"Доступно быстрых узлов: {len(checked)}"
                status_text.color = "#34D399"
                shield_ring.border = ft.border.all(2, "#38BDF8")
                shield_icon.color = "#38BDF8"
                for idx, (ping, proto, host, port, uri) in enumerate(checked):
                    label = f"[{proto}] {host}:{port} ({ping} мс)"
                    ping_color = "#34D399" if ping < 120 else ("#FBBF24" if ping < 250 else "#F87171")
                    card = ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.PUBLIC_ROUNDED, color="#38BDF8", size=22),
                                        ft.Column(
                                            controls=[
                                                ft.Text(f"{host}:{port}", size=14, weight=ft.FontWeight.W_600, color="#F1F5F9"),
                                                ft.Text(f"Протокол: {proto}", size=11, color="#94A3B8"),
                                            ],
                                            spacing=2,
                                        ),
                                    ],
                                    spacing=12,
                                ),
                                ft.Container(
                                    content=ft.Text(f"{ping} мс", size=12, weight=ft.FontWeight.BOLD, color=ping_color),
                                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                    border_radius=10,
                                    bgcolor="#0F172A",
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=12,
                        border_radius=14,
                        bgcolor="#111827",
                        border=ft.border.all(1, "#1E293B"),
                        opacity=0.0,
                        offset=ft.Offset(0, 0.15),
                        animate_opacity=ft.Animation(300 + idx * 40, ft.AnimationCurve.EASE_OUT),
                        animate_offset=ft.Animation(300 + idx * 40, ft.AnimationCurve.EASE_OUT),
                        on_click=lambda _, u=uri, l=label: select_server(u, l),
                    )
                    servers_list.controls.append(card)

            scan_btn.disabled = False
            scan_btn.opacity = 1.0
            page.update()

            for card in servers_list.controls:
                card.opacity = 1.0
                card.offset = ft.Offset(0, 0)
            page.update()

        threading.Thread(target=worker, daemon=True).start()

    scan_btn = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.RADAR_ROUNDED, color="#F8FAFC", size=20),
                ft.Text("Найти свежие IP", size=15, weight=ft.FontWeight.W_600, color="#F8FAFC"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        height=46,
        border_radius=14,
        bgcolor="#1E293B",
        border=ft.border.all(1, "#334155"),
        on_click=fetch_and_test,
        animate_opacity=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
    )

    footer = ft.Row(
        controls=[
            ft.TextButton(
                "Telegram канал",
                icon=ft.Icons.TELEGRAM,
                on_click=lambda _: page.launch_url(TG_URL),
            ),
            ft.Text("•", color="#475569"),
            ft.TextButton(
                "TikTok",
                icon=ft.Icons.MUSIC_NOTE_ROUNDED,
                on_click=lambda _: page.launch_url(TT_URL),
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    page.add(
        header,
        ft.Container(content=shield_ring, alignment=ft.alignment.center, padding=ft.padding.only(top=6, bottom=4)),
        status_text,
        scan_btn,
        active_box,
        connect_btn,
        ft.Divider(color="#1E293B", height=16),
        servers_list,
        footer,
    )


if __name__ == "__main__":
    ft.app(target=main)
