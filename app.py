import flet as ft
import threading
import time
import sys
import os

# ── make sure sibling files are importable ────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import canvas_student
import groq_bot

# ── palette ──────────────────────────────────────────────────────────────────
BG        = "#080c10"
SURFACE   = "#0d1117"
CARD      = "#111720"
BORDER    = "#1e2d3d"
RED       = "#e8413e"
RED_DIM   = "#9b1c1a"
RED_GLOW  = "#ff6b68"
TEXT      = "#e8edf2"
MUTED     = "#5a7080"
ACCENT    = "#ff6b68"

# ── helpers ───────────────────────────────────────────────────────────────────
def clean_html(raw: str) -> str:
    import re
    if not raw:
        return "Sin descripción."
    return re.sub(r"<[^>]+>", "", raw).strip() or "Sin descripción."

# ── components ────────────────────────────────────────────────────────────────
def logo_bug() -> ft.Container:
    """The little bug mascot (pure Flet shapes)."""
    return ft.Container(
        content=ft.Stack(
            controls=[
                # body
                ft.Container(
                    width=48, height=48,
                    border_radius=24,
                    bgcolor=RED,
                    left=8, top=8,
                ),
                # eyes
                ft.Container(width=10, height=10, border_radius=5,
                             bgcolor="#1a0a0a", left=14, top=20),
                ft.Container(width=10, height=10, border_radius=5,
                             bgcolor="#1a0a0a", left=40, top=20),
                # legs
                ft.Container(width=3, height=14, border_radius=2,
                             bgcolor=RED_DIM, left=4, top=38,
                             rotate=ft.Rotate(-0.4)),
                ft.Container(width=3, height=14, border_radius=2,
                             bgcolor=RED_DIM, left=57, top=38,
                             rotate=ft.Rotate(0.4)),
                ft.Container(width=3, height=18, border_radius=2,
                             bgcolor=RED_DIM, left=0, top=26,
                             rotate=ft.Rotate(-0.6)),
                ft.Container(width=3, height=18, border_radius=2,
                             bgcolor=RED_DIM, left=61, top=26,
                             rotate=ft.Rotate(0.6)),
            ],
            width=64,
            height=64,
        ),
    )


def pill_badge(text: str) -> ft.Container:
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text("NEW", size=9, weight=ft.FontWeight.W_900,
                                   color=BG),
                    bgcolor=RED,
                    border_radius=4,
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                ),
                ft.Text(text, size=12, color=MUTED),
                ft.Icon(ft.Icons.ARROW_FORWARD, size=12, color=MUTED),
            ],
            spacing=8,
            tight=True,
        ),
        border=ft.border.all(1, BORDER),
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=12, vertical=6),
        bgcolor="#0a1018",
    )


def assignment_card(name: str, desc: str) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(width=6, height=6, border_radius=3,
                                     bgcolor=RED),
                        ft.Text(name, size=13, weight=ft.FontWeight.W_700,
                                color=TEXT, expand=True),
                    ],
                    spacing=8,
                ),
                ft.Text(clean_html(desc), size=11, color=MUTED,
                        max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
            ],
            spacing=6,
        ),
        bgcolor=CARD,
        border=ft.border.all(1, BORDER),
        border_radius=10,
        padding=14,
    )


def typing_dots() -> ft.Row:
    return ft.Row(
        controls=[
            ft.Container(
                width=7, height=7, border_radius=4,
                bgcolor=RED,
                animate=ft.Animation(600, "easeInOut"),
            )
            for _ in range(3)
        ],
        spacing=5,
    )

# ── main app ──────────────────────────────────────────────────────────────────
def main(page: ft.Page):
    page.title = "CanvasBot"
    page.bgcolor = BG
    page.padding = 0
    page.fonts = {
        "Syne": "https://fonts.gstatic.com/s/syne/v22/8vIS7w4qzmVxsWxjBZRjr0FKM_04uQ.woff2",
        "DM Mono": "https://fonts.gstatic.com/s/dmmono/v14/aFTU7PB1QTsUX8KYth-QAa6JYKkJ.woff2",
    }
    page.theme = ft.Theme(font_family="DM Mono")
    page.window.width  = 420
    page.window.height = 820
    page.window.resizable = True

    # ── state ─────────────────────────────────────────────────────────────────
    # all_assignments is now a flat dict {name: desc} merged from all courses
    all_assignments: dict = {}

    # ── refs ──────────────────────────────────────────────────────────────────
    chat_column     = ft.Ref[ft.Column]()
    assignments_col = ft.Ref[ft.Column]()
    status_text     = ft.Ref[ft.Text]()
    load_btn        = ft.Ref[ft.ElevatedButton]()

    # ── chat helpers ──────────────────────────────────────────────────────────
    def bubble(text: str, is_bot: bool) -> ft.Container:
        return ft.Container(
            content=ft.Text(text, size=12, color=TEXT, selectable=True),
            bgcolor=RED if not is_bot else CARD,
            border=ft.border.all(1, BORDER if is_bot else "transparent"),
            border_radius=ft.border_radius.only(
                top_left=12, top_right=12,
                bottom_left=0 if is_bot else 12,
                bottom_right=12 if is_bot else 0,
            ),
            padding=12,
            margin=ft.margin.only(
                left=0 if is_bot else 50,
                right=50 if is_bot else 0,
                bottom=6,
            ),
        )

    def add_bubble(text: str, is_bot: bool):
        chat_column.current.controls.append(bubble(text, is_bot))
        page.update()

    # ── load assignments ──────────────────────────────────────────────────────
    def load_assignments(e):
        load_btn.current.disabled = True
        status_text.current.value = "Conectando con Canvas…"
        status_text.current.color = MUTED
        page.update()

        def _fetch():
            nonlocal all_assignments
            try:
                # getAllWeekAssignments returns a list of dicts [{name: desc}, ...]
                courses_data = canvas_student.getAllWeekAssignments()

                # Flatten all courses into a single dict
                all_assignments = {}
                for course_dict in courses_data:
                    all_assignments.update(course_dict)

                assignments_col.current.controls.clear()

                if all_assignments:
                    for name, desc in all_assignments.items():
                        assignments_col.current.controls.append(
                            assignment_card(name, desc)
                        )
                    status_text.current.value = f"✓  {len(all_assignments)} tareas pendientes"
                    status_text.current.color = "#4caf87"
                else:
                    assignments_col.current.controls.append(
                        ft.Container(
                            content=ft.Text("¡Sin tareas esta semana! 🎉",
                                            size=12, color=MUTED,
                                            text_align=ft.TextAlign.CENTER),
                            alignment=ft.Alignment(0, 0),
                            padding=30,
                        )
                    )
                    status_text.current.value = "Sin tareas pendientes"
                    status_text.current.color = "#4caf87"

            except Exception as ex:
                status_text.current.value = f"Error: {ex}"
                status_text.current.color = RED
            finally:
                load_btn.current.disabled = False
                page.update()

        threading.Thread(target=_fetch, daemon=True).start()

    # ── ask AI ────────────────────────────────────────────────────────────────
    def ask_ai(e):
        if not all_assignments:
            add_bubble("⚠  Primero carga tus tareas.", True)
            return

        add_bubble("Analiza mis tareas y dame un resumen.", False)

        def _run():
            dots = ft.Container(
                content=ft.Row(
                    [ft.Container(width=6, height=6, border_radius=3, bgcolor=RED)
                     for _ in range(3)],
                    spacing=4,
                ),
                padding=12,
                bgcolor=CARD,
                border_radius=10,
                margin=ft.margin.only(right=50, bottom=6),
            )
            chat_column.current.controls.append(dots)
            page.update()

            try:
                # startChatBot() fetches all courses internally — no args needed
                result = groq_bot.startChatBot()

                chat_column.current.controls.remove(dots)
                live_text = ft.Text("", size=12, color=TEXT, selectable=True)
                live_bubble = ft.Container(
                    content=live_text,
                    bgcolor=CARD,
                    border=ft.border.all(1, BORDER),
                    border_radius=ft.border_radius.only(
                        top_left=12, top_right=12,
                        bottom_left=0, bottom_right=12,
                    ),
                    padding=12,
                    margin=ft.margin.only(right=50, bottom=6),
                )
                chat_column.current.controls.append(live_bubble)
                add_bubble(result,True)
                page.update()

                       

            except Exception as ex:
                if dots in chat_column.current.controls:
                    chat_column.current.controls.remove(dots)
                add_bubble(f"❌ Error al conectar con Groq: {ex}", True)

        threading.Thread(target=_run, daemon=True).start()

    # ── chat input ────────────────────────────────────────────────────────────
    chat_input = ft.TextField(
        hint_text="Pregúntame algo sobre tus tareas…",
        hint_style=ft.TextStyle(color=MUTED, size=12),
        text_style=ft.TextStyle(color=TEXT, size=12, font_family="DM Mono"),
        border=ft.InputBorder.NONE,
        expand=True,
        bgcolor="transparent",
        cursor_color=RED,
        on_submit=lambda e: _send_custom(e),
    )

    def _send_custom(e):
        msg = chat_input.value.strip()
        if not msg:
            return
        chat_input.value = ""
        add_bubble(msg, False)

        def _reply():
            time.sleep(0.8)
            add_bubble(
                "Aún estoy aprendiendo a responder eso 🤖. "
                "Por ahora usa el botón de resumen para analizar tus tareas.",
                True,
            )

        threading.Thread(target=_reply, daemon=True).start()

    # ── HEADER ────────────────────────────────────────────────────────────────
    header = ft.Container(
        content=ft.Column(
            controls=[
                logo_bug(),
                ft.Text("CanvasBot", size=32, weight=ft.FontWeight.W_900,
                        color=TEXT, font_family="Syne"),
                ft.Text("THE AI THAT ACTUALLY DOES HOMEWORK.",
                        size=10, weight=ft.FontWeight.W_700,
                        color=RED,
                        style=ft.TextStyle(letter_spacing=2)),
                ft.Text("Analiza tus tareas en Canvas, genera resúmenes\n"
                        "y responde tus dudas con IA.",
                        size=12, color=MUTED, text_align=ft.TextAlign.CENTER),
                pill_badge("Powered by Groq · llama-3.3-70b"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        padding=ft.padding.symmetric(vertical=32, horizontal=20),
        alignment=ft.Alignment(0, 0),
        gradient=ft.LinearGradient(
            begin=ft.Alignment(0, -1),
            end=ft.Alignment(0, 1),
            colors=[SURFACE, BG],
        ),
    )

    # ── LOAD PANEL (button only, no text field) ───────────────────────────────
    load_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.ElevatedButton(
                     "Cargar mis tareas",
                    ref=load_btn,
                    icon=ft.Icons.DOWNLOAD_ROUNDED,
                    on_click=load_assignments,
                    style=ft.ButtonStyle(
                        color=TEXT,
                        bgcolor={"": CARD, "hovered": RED_DIM},
                        side=ft.BorderSide(1, BORDER),
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.padding.symmetric(horizontal=20, vertical=14),
                    ),
                    expand=True,
                ),
                ft.Text(ref=status_text, value="", size=11, color=MUTED),
            ],
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=10),
    )

    # ── TABS ──────────────────────────────────────────────────────────────────
    selected_tab = {"v": 0}

    tab_assignments_view = ft.Column(
        ref=assignments_col,
        controls=[
            ft.Container(
                content=ft.Text("Presiona \"Cargar mis tareas\" para ver las tareas.",
                                size=12, color=MUTED,
                                text_align=ft.TextAlign.CENTER),
                alignment=ft.Alignment(0, 0),
                padding=30,
            )
        ],
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
    )

    tab_chat_view = ft.Column(
        controls=[
            ft.Container(
                content=ft.Column(
                    ref=chat_column,
                    controls=[
                        ft.Container(
                            content=ft.Text(
                                "Hola 👋  Carga tus tareas y presiona\n"
                                "\"Resumir\" para analizarlas.",
                                size=12, color=MUTED,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            alignment=ft.Alignment(0, 0),
                            padding=20,
                        )
                    ],
                    spacing=4,
                    scroll=ft.ScrollMode.AUTO,
                ),
                expand=True,
                height=340,
            ),
            ft.Divider(height=1, color=BORDER),
            ft.Container(
                content=ft.Row(
                    controls=[
                        chat_input,
                        ft.IconButton(
                            icon=ft.Icons.AUTO_AWESOME_ROUNDED,
                            icon_color=RED,
                            icon_size=18,
                            tooltip="Resumir tareas",
                            on_click=ask_ai,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.SEND_ROUNDED,
                            icon_color=MUTED,
                            icon_size=18,
                            tooltip="Enviar",
                            on_click=_send_custom,
                        ),
                    ],
                ),
                bgcolor=CARD,
                border=ft.border.all(1, BORDER),
                border_radius=10,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                margin=ft.margin.only(top=8),
            ),
        ],
        spacing=0,
    )

    tab_bar_items = ["Tareas", "Chat IA"]
    tab_indicators = []
    tab_labels     = []

    def switch_tab(idx: int):
        selected_tab["v"] = idx
        for i, (ind, lbl) in enumerate(zip(tab_indicators, tab_labels)):
            ind.bgcolor = RED if i == idx else "transparent"
            lbl.color   = TEXT if i == idx else MUTED
        switcher.content = [tab_assignments_view, tab_chat_view][idx]
        page.update()

    for idx, label in enumerate(tab_bar_items):
        ind = ft.Container(height=2, border_radius=1,
                           bgcolor=RED if idx == 0 else "transparent",
                           animate=ft.Animation(200, "ease"))
        lbl = ft.Text(label, size=12, weight=ft.FontWeight.W_700,
                      color=TEXT if idx == 0 else MUTED,
                      animate_opacity=ft.Animation(200, "ease"))
        tab_indicators.append(ind)
        tab_labels.append(lbl)

    def _make_tab_btn(idx):
        return ft.GestureDetector(
            content=ft.Column(
                controls=[tab_labels[idx], tab_indicators[idx]],
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            on_tap=lambda e, i=idx: switch_tab(i),
        )

    tab_bar = ft.Container(
        content=ft.Row(
            controls=[_make_tab_btn(i) for i in range(len(tab_bar_items))],
            spacing=24,
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=8),
        border=ft.border.only(bottom=ft.border.BorderSide(1, BORDER)),
    )

    switcher = ft.AnimatedSwitcher(
        content=tab_assignments_view,
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=200,
    )

    # ── ROOT LAYOUT ───────────────────────────────────────────────────────────
    page.add(
        ft.Column(
            controls=[
                header,
                load_panel,
                tab_bar,
                ft.Container(
                    content=switcher,
                    padding=ft.padding.symmetric(horizontal=20, vertical=10),
                    expand=True,
                ),
            ],
            spacing=0,
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )
    )

    # subtle star-field background shimmer via page overlay (cosmetic)
    page.overlay.append(
        ft.Container(
            width=page.window.width,
            height=4,
            top=0,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0),
                end=ft.Alignment(1, 0),
                colors=[BG, RED_DIM, BG],
            ),
        )
    )
    page.update()


ft.app(target=main)