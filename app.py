import flet as ft
import sys
sys.path.append(".")  # makes sure Python finds your files
import canvas_student
from groq_bot import startChatBot

def main(page: ft.Page):
    page.title = "CanvasBot"
    page.bgcolor = "#080d12"
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    page.fonts = {
        "Mono": "https://fonts.gstatic.com/s/spacemono/v13/i7dPIFZifjKcF5UAWdDRYEF8RQ.woff2"
    }

    # ── Glow helper ───────────────────────────────────────────────────────────
    def glowing(content, color="#4a9eff", radius=14, blur=24):
        return ft.Container(
            content=content,
            border_radius=radius,
            shadow=[
                ft.BoxShadow(blur_radius=blur,     spread_radius=1, color=f"{color}66", offset=ft.Offset(0, 0)),
                ft.BoxShadow(blur_radius=blur * 2, spread_radius=2, color=f"{color}33", offset=ft.Offset(0, 0)),
                ft.BoxShadow(blur_radius=blur * 3, spread_radius=3, color=f"{color}11", offset=ft.Offset(0, 0)),
            ],
        )

    # ── State ─────────────────────────────────────────────────────────────────
    assignments_list = ft.Row(wrap=True, spacing=16, run_spacing=16)

    # ── Handlers ──────────────────────────────────────────────────────────────
    def on_search(e):
        code = course_input.value.strip()
        if not code:
            return

        assignments_list.controls.clear()
        results_section.visible = True

        assignments = startChatBot(code)

        for a in assignments:
            due = a["due_at"][:10]
            pts = a.get("points_possible")
            pts_str = f"{int(pts)} pts" if pts else "ungraded"

            card = ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Text("DUE", size=10, color="#4a9eff", weight="bold", font_family="Mono"),
                            bgcolor="#0d1f35",
                            border_radius=4,
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                        ),
                        ft.Text(a["name"], size=15, weight="bold", color="#ffffff"),
                        ft.Text(f"📅 {due}", size=12, color="#556677"),
                        ft.Text(f"⭐ {pts_str}", size=12, color="#556677"),
                    ],
                    spacing=8,
                ),
                width=220,
                bgcolor="#0e1520",
                border_radius=14,
                padding=20,
                border=ft.border.all(1, "#1a3050"),
                shadow=[
                    ft.BoxShadow(blur_radius=16, spread_radius=1, color="#4a9eff22", offset=ft.Offset(0, 0)),
                    ft.BoxShadow(blur_radius=32, spread_radius=2, color="#4a9eff11", offset=ft.Offset(0, 0)),
                ],
            )
            assignments_list.controls.append(card)

        section_label.value = f"Assignments for  {code}"
        page.update()

    def on_clear(e):
        course_input.value = ""
        assignments_list.controls.clear()
        results_section.visible = False
        page.update()

    # ── Bot mascot ────────────────────────────────────────────────────────────
    bot_inner = ft.Column(
        [
            ft.Row(
                [ft.Container(width=3, height=14, bgcolor="#4a9eff", border_radius=2)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [ft.Container(width=10, height=10, bgcolor="#4a9eff", border_radius=5)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Container(
                                    content=ft.Container(width=5, height=5, bgcolor="#4a9eff", border_radius=3),
                                    width=16, height=16, bgcolor="#080d12", border_radius=8,
                                    alignment=ft.alignment.Alignment(0, 0),
                                ),
                                ft.Container(
                                    content=ft.Container(width=5, height=5, bgcolor="#4a9eff", border_radius=3),
                                    width=16, height=16, bgcolor="#080d12", border_radius=8,
                                    alignment=ft.alignment.Alignment(0, 0),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=14,
                        ),
                        ft.Row(
                            [ft.Container(width=24, height=4, bgcolor="#080d12", border_radius=2)],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                width=72,
                height=60,
                bgcolor="#2a6fd6",
                border_radius=ft.border_radius.only(top_left=16, top_right=16, bottom_left=8, bottom_right=8),
            ),
            ft.Container(
                content=ft.Row(
                    [
                        ft.Container(width=12, height=20, bgcolor="#2a6fd6", border_radius=4),
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Container(width=8, height=8, bgcolor="#4a9eff", border_radius=4),
                                    ft.Container(width=8, height=8, bgcolor="#1a4fa0", border_radius=4),
                                ],
                                spacing=4,
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            width=40, height=30, bgcolor="#1a4fa0", border_radius=6,
                        ),
                        ft.Container(width=12, height=20, bgcolor="#2a6fd6", border_radius=4),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=3,
                ),
                width=72,
                height=36,
            ),
            ft.Row(
                [
                    ft.Container(width=14, height=16, bgcolor="#2a6fd6",
                                 border_radius=ft.border_radius.only(bottom_left=6, bottom_right=6)),
                    ft.Container(width=14, height=16, bgcolor="#2a6fd6",
                                 border_radius=ft.border_radius.only(bottom_left=6, bottom_right=6)),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
    )

    # Wrap bot in glow
    bot = ft.Container(
        content=bot_inner,
        shadow=[
            ft.BoxShadow(blur_radius=40, spread_radius=0, color="#1a6fffaa", offset=ft.Offset(0, 0)),
            ft.BoxShadow(blur_radius=80, spread_radius=0, color="#1a6fff44", offset=ft.Offset(0, 0)),
            ft.BoxShadow(blur_radius=120, spread_radius=0, color="#1a6fff22", offset=ft.Offset(0, 0)),
        ],
    )

    # ── Input ─────────────────────────────────────────────────────────────────
    course_input = ft.TextField(
    hint_text="Enter course code  e.g. P2026_ESI3119C",
    hint_style=ft.TextStyle(color="#2a3545"),
    text_style=ft.TextStyle(color="#ffffff", size=13, font_family="Mono"),  # make sure white
    bgcolor="#0e1520",
    border_color="#1a2535",
    focused_border_color="#4a9eff",
    border_radius=10,
    height=52,
    expand=True,
    on_submit=on_search,
    cursor_color="#4a9eff",
    color="#ffffff",  )

    search_btn = ft.ElevatedButton(
        "FETCH →",
        on_click=on_search,
        bgcolor="#4a9eff",
        color="#080d12",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            text_style=ft.TextStyle(weight="bold", size=12, font_family="Mono"),
            shadow_color="#4a9eff",
            elevation=12,
        ),
        height=52,
        width=100,
    )

    section_label = ft.Text("", size=13, color="#555", font_family="Mono")

    results_section = ft.Column(
        [
            ft.Row(
                [
                    ft.Row([
                        ft.Text("›", size=20, color="#4a9eff", weight="bold"),
                        section_label,
                    ], spacing=6),
                    ft.TextButton("clear", on_click=on_clear,
                                  style=ft.ButtonStyle(color="#2a3545")),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            assignments_list,
        ],
        visible=False,
        spacing=16,
    )

    # ── Layout ────────────────────────────────────────────────────────────────
    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Container(height=40),
                    ft.Row([bot], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(height=20),
                    ft.Row(
                        [
                            ft.Text("Canvas", size=40, weight="bold", color="#ffffff"),
                            ft.Text("Bot", size=40, weight="bold", color="#4a9eff",
                                    spans=[ft.TextSpan(style=ft.TextStyle(shadow=[
                                        ft.BoxShadow(blur_radius=20, color="#4a9eff99", offset=ft.Offset(0, 0)),
                                        ft.BoxShadow(blur_radius=40, color="#4a9eff44", offset=ft.Offset(0, 0)),
                                    ]))]),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    ft.Row(
                        [ft.Text("YOUR ASSIGNMENTS. FETCHED INSTANTLY.", size=11,
                                 color="#4a9eff", weight="bold", font_family="Mono")],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Container(height=8),
                    ft.Row(
                        [ft.Text("Enter your Canvas course code and get all upcoming assignments.",
                                 size=13, color="#334455", text_align=ft.TextAlign.CENTER)],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Container(height=32),
                    ft.Row([course_input, search_btn], spacing=10),
                    ft.Container(height=32),
                    ft.Divider(color="#0e1520", height=1),
                    ft.Container(height=24),
                    results_section,
                ],
                spacing=6,
            ),
            padding=ft.padding.symmetric(horizontal=48, vertical=0),
            expand=True,
        )
    )


ft.app(target=main)