import socket
import threading
import time
import re
import flet as ft
import requests

SOURCES = [
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/Sub1.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/ebbiner/V2ray-configs/main/V2ray_configs.txt",
]

TG_URL = "https://t.me/Ars3nbar_osn"
TT_URL = "https://www.tiktok.com/@ars3nbar"

THEMES = {
    "Cyber Blue": {"primary": "#38BDF8", "secondary": "#818CF8", "bg": "#060913", "card": "#0F172A"},
    "Neon Purple": {"primary": "#C084FC", "secondary": "#F472B6", "bg": "#0A0612", "card": "#160E26"},
    "Matrix Green": {"primary": "#34D399", "secondary": "#2DD4BF", "bg": "#050908", "card": "#0D1614"},
    "Crimson Red": {"primary": "#F87171", "secondary": "#FB8B85", "bg": "#0F0608", "card": "#1C0D11"},
}


def parse_node(uri: str):
    try:
        proto = uri.split("://", 1)[0].upper()
        remark = "Global Node"
        if "#" in uri:
            remark = requests.utils.unquote(uri.split("#", 1)[1]).strip()
            remark = re.sub(r'[\x00-\x1f]', '', remark)[:26] or "Global Node"
        if "@" in uri:
            after_at = uri.split("@", 1)[1]
            host_port = after_at.split("?", 1)[0].split("#", 1)[0]
            if ":" in host_port:
                host, port = host_port.rsplit(":", 1)
                return proto, host.strip("[]"), int(port), remark
    except Exception:
        pass
    return None, None, None, None


def check_ping(host: str, port: int, timeout: float = 1.4):
    start = time.time()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return int((time.time() - start) * 1000)
    except Exception:
        return None


def main(page: ft.Page):
    state = {
        "theme": "Cyber Blue",
        "filter": "ALL",
        "selected_uri": "",
        "nodes": [],
        "scanning": False,
    }

    th = THEMES[state["theme"]]
    page.title = "ABvpn 2.0"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = th["bg"]
    page.window.width = 440
    page.window.height = 760
    page.padding = 18

    core_icon = ft.Icon(ft.Icons.SHIELD_MOON_ROUNDED, color=th["primary"], size=46)
    core_label = ft.Text("SCAN", size=11, weight=ft.FontWeight.BOLD, color="#F8FAFC")

    inner_core = ft.Container(
        content=ft.Column(
            [core_icon, core_label],
            alignment=ft.MainAxisAlignment.CENTER,,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
        ),
        width=108,
        height=108,
        border_radius=54,
        bgcolor=th["card"],
        border=ft.border.all(2, th["primary"]),
        alignment=ft.alignment.center,
        scale=ft.Scale(1.0),
        animate_scale=ft.Animation(450, ft.AnimationCurve.EASE_IN_OUT),
        animate=ft.Animation(450, ft.AnimationCurve.EASE_IN_OUT),
        shadow=ft.BoxShadow(blur_radius=28, color=th["primary"] + "55"),
    )

    outer_ring = ft.Container(
        content=inner_core,
        width=134,
        height=134,
        border_radius=67,
        border=ft.border.all(1.5, th["secondary"] + "66"),
        alignment=ft.alignment.center,
        scale=ft.Scale(1.0),
        animate_scale=ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT),
        animate=ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT),
    )

    status_badge = ft.Text("Нажми на реактор для поиска услов", size=13, color="#94A3B8", text_align=ft.TextAlign.CENTER)

    active_title = ft.Text("Узел не выбран", size=13, weight=ft.FontWeight.W600, color="#F1F5F9")
    active_sub = ft.Text("Выберите сервер из списка ниже", size=11, color="#64748B")

    def copy_key(e):
        if state["selected_uri"]:
            page.set_clipboard(state["selected_uri"])
            status_badge.value = "Протокол в буфере обмена!"
            status_badge.color = "#34D399"
            inner_core.scale = ft.Scale(1.15)
            outer_ring.scale = ft.Scale(1.08)
            page.update()
            time.sleep(0.3)
            inner_core.scale = ft.Scale(1.0)
            outer_ring.scale = ft.Scale(1.0)
            page.update()

    copy_btn = ft.Container(
        content=ft.Row(
            [ft.Icon(ft.Icons.COPY_ALL_ROUNDED, color="#060913", size=18), ft.Text("СКОПИРОВАТЬ КЛЮЧ", size=13, weight=ft.FontWeight.BOLD, color="#060913")],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        height=44,
        border_radius=12,
        gradient=ft.LinearGradient(colors=[th["primary"], th["secondary"]]),
        opacity=0.35,
        disabled=True,
        on_click=copy_key,
        animate_opacity=ft.Animation(250),
    )

    active_card = ft.Container(
        content=ft.Column([active_title, active_sub, copy_btn], spacing=8),
        padding=14,
        border_radius=16,
        bgcolor=th["card"],
        border=ft.border.all(1, th["primary"] + "44"),
        animate=ft.Animation(300),
    )

    servers_list = ft.ListView(expand=True, spacing=8)

    def select_node(node):
        ping, proto, host, port, remark, uri = node
        state["selected_uri"] = uri
        active_title.value = f"[{proto}] {remark} • {ping} мс"
        active_sub.value = f"{host}:{port}"
        copy_btn.disabled = False
        copy_btn.opacity = 1.0
        page.update()

    def render_nodes():
        servers_list.controls.clear()
        cur_th = THEMES[state["theme"]]
        filtered = [
            n for n in state["nodes"]
            if state["filter"] == "ALL" or n[1] == state["filter"]
        ]
        for idx, n in enumerate(filtered):
            ping, proto, host, port, remark, uri = n
            p_color = "#34D399" if ping < 130 else ("#FBBF24" if ping < 260 else "#F87171")
            card = ft.Container(
                content=ft.Row(
                    [
                        ft.Row(
                            [
                                ft.Container(
                                    content=ft.Text(proto[:4], size=10, weight=ft.FontWeight.BOLD, color=cur_th["primary"]),
                                    padding=ft.padding.symmetric(horizontal=7, vertical=4),
                                    border_radius=8,
                                    bgcolor=cur_th["primary"] + "22",
                                ),
                                ft.Column(
                                    [
                                        ft.Text(remark, size=13, weight=ft.FontWeight.W600, color="#F1F5F9"),
                                        ft.Text(f"{host}:{port}", size=11, color="#64748B"),
                                    ],
                                    spacing=1,
                                ),
                            ],
                            spacing=10,
                        ),
                        ft.Text(f"{ping} ms", size=12, weight=ft.FontWeight.BOLD, color=p_color),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=11,
                border_radius=13,
                bgcolor=cur_th["card"],
                border=ft.border.all(1, cur_th["primary"] + "22"),
                on_click=lambda _, node=n: select_node(node),
            )
            servers_list.controls.append(card)
        page.update()

    def start_scan(e):
        if state["scanning"]:
            return
        state["scanning"] = True
        core_label.value = "SCANNING"
        inner_core.scale = ft.Scale(1.12)
        outer_ring.scale = ft.Scale(1.15)
        status_badge.value = "Сканируем узлы и замеряем пинг..."
        status_badge.color = "#FBBF24"
        page.update()

        def worker():
            raw_list = []
            for url in SOURCES:
                try:
                    r = requests.get(url, timeout=7)
                    if r.status_code == 200:
                        for l in r.text.splitlines():
                            l = l.strip()
                            if l.startswith(("vless://", "trojan://", "ss://")):
                                raw_list.append(l)
                except Exception:
                    continue

            found = []
            for uri in raw_list[:90]:
                proto, host, port, remark = parse_node(uri)
                if host and port:
                    ping = check_ping(host, port)
                    if ping is not None:
                        found.append((ping, proto, host, port, remark, uri))
                if len(found) >= 20:
                    break

            found.sort(key=lambda x: x[0])
            state["nodes"] = found
            state["scanning"] = False
            core_label.value = "READY"
            inner_core.scale = ft.Scale(1.0)
            outer_ring.scale = ft.Scale(1.0)
            if found:
                status_badge.value = f"Активных узлов: {len(found)}"
                status_badge.color = "#34D399"
            else:
                status_badge.value = "Серверы не ответили. Повторите."
                status_badge.color = "#F87171"
            render_nodes()

        threading.Thread(target=worker, daemon=True).start()

    outer_ring.on_click = start_scan

    def set_filter(f):
        state["filter"] = f
        for chip in filter_row.controls:
            chip.selected = (chip.label.value == f)
        render_nodes()

    filter_row = ft.Row(
        [
            ft.Chip(label=ft.Text(f""), selected=(f == "ALL"), on_select=lambda _, v=f: set_filter(v))
            for f in ["ALL", "VLESS", "TROJAN", "SS"]
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=6,
    )

    ip_input = ft.TextField(label="IP-адрес или домен", hint_text="185.220.101.1", border_radius=12)
    port_input = ft.TextField(label="П
