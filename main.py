# main.py
import sys
import json
from pathlib import Path

import customtkinter as ctk
from tkinter import messagebox, StringVar, IntVar

from data_handler import load_progress, save_progress
from questions import get_all_questions, delete_question, get_random_question


# ============================================================
# UIv2 — НАСТРОЙКИ ТЕМЫ
# ============================================================
PRIMARY_BG = "#121212" # Фон приложения
PANEL_BG   = "#1A1A1A" # Фон панелей / sidebar
CARD_BG    = "#1E1E1E" # Фон карточек
BORDER_CLR = "#2A2A2A" # Рамки
ACCENT     = "#0E7C7B" # Акцентные кнопки
TEXT_MAIN  = "#FFFFFF" # Основной текст
TEXT_MUTED = "#B0B0B0" # Приглушённый текст


# ============================================================
# БОКОВАЯ ПАНЕЛЬ (Sidebar)
# ============================================================
class SidebarV2(ctk.CTkFrame):
    """Боковая панель навигации с возможностью сворачивания"""
    def __init__(self, master, on_nav):
        super().__init__(master, fg_color=PANEL_BG)

        self.on_nav = on_nav

        self.expanded_width = 260
        self.collapsed_width = 72
        self.is_expanded = True

        self.configure(width=self.expanded_width)
        self.pack_propagate(False)
        # Заголовок с иконкой
        header = ctk.CTkLabel(
            self,
            text="🎸",
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header.pack(pady=(16, 8))
        # Кнопка сворачивания панели
        self.toggle_btn = ctk.CTkButton(
            self,
            text="⋘⋙",
            width=40,
            height=32,
            fg_color=PANEL_BG,
            hover_color="#242424",
            text_color=TEXT_MUTED,
            corner_radius=9,
            command=self.toggle
        )
        self.toggle_btn.pack(pady=(0, 12))
        # Контейнер для кнопок навигации
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(fill="both", expand=True, pady=(8, 8))

        self.buttons = []
        self.active_action = "home"
        # Добавляем кнопки навигации
        self.add_nav_button("🏠", "На главную", "home")
        self.add_nav_button("➕", "Добавить вопрос", "add")
        self.add_nav_button("🗑", "Удалить вопрос", "delete")
        self.add_nav_button("📄", "Список вопросов", "list")
        # Нижняя часть панели (выход)
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(fill="x", side="bottom", pady=12)

        self.exit_btn = ctk.CTkButton(
            self.bottom_frame,
            text="⏻  Выход из игры",
            anchor="w",
            height=36,
            fg_color=PANEL_BG,
            hover_color="#242424",
            text_color="#FF6B6B",
            corner_radius=10,
            command=self.on_exit_click
        )
        self.exit_btn.pack(fill="x", padx=12)

        self.update_layout()

    def add_nav_button(self, icon, text, action):
        """Добавляет кнопку навигации"""
        btn = ctk.CTkButton(
            self.nav_frame,
            text=f"{icon}  {text}",
            anchor="w",
            height=38,
            fg_color=PANEL_BG,
            hover_color="#242424",
            text_color=TEXT_MUTED,
            corner_radius=10,
            command=lambda a=action: self.handle_nav(a)
        )
        btn.pack(fill="x", padx=12, pady=4)
        self.buttons.append((btn, icon, text, action))

    def handle_nav(self, action):
        """Обрабатывает нажатие кнопки навигации"""
        self.active_action = action
        self.update_active_state()
        self.on_nav(action)

    def update_active_state(self):
        """Подсвечивает активную кнопку"""
        for btn, icon, text, action in self.buttons:
            if action == self.active_action:
                btn.configure(
                    fg_color="#242424",
                    text_color=TEXT_MAIN
                )
            else:
                btn.configure(
                    fg_color=PANEL_BG,
                    text_color=TEXT_MUTED
                )

    def on_exit_click(self):
        """Выход из приложения"""
        self.on_nav("exit")

    def toggle(self):
        """Сворачивает / разворачивает боковую панель"""
        self.is_expanded = not self.is_expanded
        self.update_layout()

    def update_layout(self):
        """Обновляет ширину и текст кнопок при сворачивании"""
        new_width = self.expanded_width if self.is_expanded else self.collapsed_width
        self.configure(width=new_width)

        for btn, icon, text, action in self.buttons:
            if self.is_expanded:
                btn.configure(text=f"{icon}  {text}", anchor="w")
            else:
                btn.configure(text=icon, anchor="center")

        if self.is_expanded:
            self.exit_btn.configure(text="⏻  Выход из игры", anchor="w")
        else:
            self.exit_btn.configure(text="⏻", anchor="center")

        self.master.update_idletasks()


# ============================================================
# ОСНОВНОЕ ПРИЛОЖЕНИЕ
# ============================================================
class GuitarQuizAppV2(ctk.CTk):
    """Главный класс приложения"""
    def __init__(self):
        super().__init__()

        self.title("🎸 Нотный квиз — UI v2")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        self.resizable(True, True)

        self.configure(fg_color=PRIMARY_BG)

        self.progress = load_progress()
        if "wrong_answers" not in self.progress:
            self.progress["wrong_answers"] = []
        if "hero_level" not in self.progress:
            self.progress["hero_level"] = "Новичок"

        self.main_container = ctk.CTkFrame(self, fg_color=PRIMARY_BG)
        self.main_container.pack(fill="both", expand=True)

        self.sidebar = SidebarV2(self.main_container, self.handle_nav)
        self.sidebar.pack(side="left", fill="y")

        self.content_frame = ctk.CTkFrame(self.main_container, fg_color=PRIMARY_BG)
        self.content_frame.pack(side="left", fill="both", expand=True)

        self.show_dashboard()

    # ------------------------------------------------------------
    # Навигация
    # ------------------------------------------------------------
    def handle_nav(self, action: str):
        """Центральная навигация между экранами"""
        if action == "home":
            self.show_dashboard()
        elif action == "add":
            self.show_add_question_screen()
        elif action == "delete":
            self.show_delete_question_screen()
        elif action == "list":
            self.show_question_list()
        elif action == "exit":
            self.quit_app()

    def clear_content(self):
        """Очищает область основного контента"""
        for w in self.content_frame.winfo_children():
            w.destroy()

    # ============================================================
    # ГЛАВНАЯ ПАНЕЛЬ (Dashboard)
    # ============================================================
    def show_dashboard(self):
        self.clear_content()

        wrapper = ctk.CTkFrame(self.content_frame, fg_color=PRIMARY_BG)
        wrapper.pack(fill="both", expand=True, padx=32, pady=32)

        title = ctk.CTkLabel(
            wrapper,
            text="Главная панель",
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 24))

        row1 = ctk.CTkFrame(wrapper, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 24))

        def make_card(parent, title, value):
            card = ctk.CTkFrame(
                parent,
                fg_color=CARD_BG,
                corner_radius=14,
                border_width=1,
                border_color=BORDER_CLR,
                height=120
            )
            card.pack(side="left", fill="x", expand=True, padx=8)

            ctk.CTkLabel(
                card,
                text=title,
                text_color=TEXT_MUTED,
                font=ctk.CTkFont(size=16)
            ).pack(anchor="w", padx=20, pady=(16, 4))

            ctk.CTkLabel(
                card,
                text=value,
                text_color=TEXT_MAIN,
                font=ctk.CTkFont(size=32, weight="bold")
            ).pack(anchor="w", padx=20)

            return card

        make_card(row1, "Звёзды", str(self.progress["total_stars"]))
        make_card(row1, "Жизни", str(self.progress["lives"]))
        level_card = make_card(row1, "Уровень", self.progress["hero_level"])
        # Прогресс-бар уровня
        need = 100
        current = self.progress["total_stars"] % need
        percent = current / need

        progress_bar = ctk.CTkProgressBar(
            level_card,
            width=260,
            height=10,
            progress_color=ACCENT
        )
        progress_bar.pack(anchor="w", padx=20, pady=(8, 0))
        progress_bar.set(percent)

        ctk.CTkLabel(
            level_card,
            text=f"{current} / {need} до следующего уровня",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", padx=20, pady=(4, 12))

        row2 = ctk.CTkFrame(wrapper, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 24))

        make_card(row2, "Правильные ответы", str(self.progress["correct_answers"]))
        make_card(row2, "Неправильные ответы", str(len(self.progress.get("wrong_answers", []))))
        # Кнопка "Начать игру"
        play_card = ctk.CTkFrame(
            wrapper,
            fg_color=CARD_BG,
            corner_radius=16,
            border_width=1,
            border_color=BORDER_CLR,
            height=200
        )
        play_card.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            play_card,
            text="Начать игру",
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=(28, 12))

        ctk.CTkButton(
            play_card,
            text="Играть",
            fg_color=ACCENT,
            hover_color="#0B5F5E",
            text_color="white",
            corner_radius=14,
            width=260,
            height=52,
            font=ctk.CTkFont(size=20, weight="bold"),
            command=self.start_quiz_screen
        ).pack()

    # ============================================================
    # ЭКРАН ДОБАВЛЕНИЯ ВОПРОСА
    # ============================================================
    def show_add_question_screen(self):
        self.clear_content()

        wrapper = ctk.CTkFrame(self.content_frame, fg_color=PRIMARY_BG)
        wrapper.pack(fill="both", expand=True, padx=32, pady=32)

        title = ctk.CTkLabel(
            wrapper,
            text="Добавить новый вопрос",
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 24))

        q_label = ctk.CTkLabel(
            wrapper,
            text="Текст вопроса",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=15)
        )
        q_label.pack(anchor="w")

        self.q_entry = ctk.CTkEntry(
            wrapper,
            height=42,
            fg_color=PRIMARY_BG,
            border_color=BORDER_CLR,
            border_width=1,
            text_color=TEXT_MAIN,
            placeholder_text="Введите ваш вопрос здесь..."
        )
        self.q_entry.pack(fill="x", pady=(6, 24))

        answers_title = ctk.CTkLabel(
            wrapper,
            text="Варианты ответов (отметьте правильный)",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=15)
        )
        answers_title.pack(anchor="w", pady=(0, 12))

        self.answer_frame = ctk.CTkFrame(wrapper, fg_color="transparent")
        self.answer_frame.pack(fill="x")

        self.answer_vars = []
        self.correct_var = IntVar(value=0)

        def add_answer_field():
            idx = len(self.answer_vars)

            row = ctk.CTkFrame(self.answer_frame, fg_color="transparent")
            row.pack(fill="x", pady=6)

            radio = ctk.CTkRadioButton(
                row,
                text="",
                variable=self.correct_var,
                value=idx,
                fg_color=ACCENT,
                border_color=BORDER_CLR,
                text_color=TEXT_MAIN
            )
            radio.pack(side="left", padx=(0, 12))

            entry = ctk.CTkEntry(
                row,
                height=40,
                fg_color=PRIMARY_BG,
                border_color=BORDER_CLR,
                border_width=1,
                text_color=TEXT_MAIN,
                placeholder_text=f"Вариант ответа {idx+1}"
            )
            entry.pack(side="left", fill="x", expand=True)

            self.answer_vars.append(entry)

        for _ in range(4):
            add_answer_field()

        add_btn = ctk.CTkButton(
            wrapper,
            text="+ Добавить ещё вариант",
            fg_color=PANEL_BG,
            hover_color="#242424",
            text_color=TEXT_MUTED,
            corner_radius=10,
            height=38,
            command=add_answer_field
        )
        add_btn.pack(anchor="w", pady=(12, 32))

        settings_title = ctk.CTkLabel(
            wrapper,
            text="Настройки",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=15)
        )
        settings_title.pack(anchor="w", pady=(0, 12))

        settings_row = ctk.CTkFrame(wrapper, fg_color="transparent")
        settings_row.pack(fill="x")

        time_frame = ctk.CTkFrame(settings_row, fg_color="transparent")
        time_frame.pack(side="left", fill="x", expand=True, padx=(0, 12))

        ctk.CTkLabel(
            time_frame,
            text="Время на ответ",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w")

        self.time_var = StringVar(value="30 сек")
        ctk.CTkOptionMenu(
            time_frame,
            values=["10 сек", "20 сек", "30 сек", "60 сек"],
            variable=self.time_var,
            fg_color=PANEL_BG,
            button_color=PANEL_BG,
            button_hover_color="#242424",
            text_color=TEXT_MAIN
        ).pack(fill="x", pady=6)

        score_frame = ctk.CTkFrame(settings_row, fg_color="transparent")
        score_frame.pack(side="left", fill="x", expand=True, padx=(12, 0))

        ctk.CTkLabel(
            score_frame,
            text="Очки за правильный ответ",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w")

        self.score_var = StringVar(value="10")
        ctk.CTkOptionMenu(
            score_frame,
            values=["5", "10", "15", "20"],
            variable=self.score_var,
            fg_color=PANEL_BG,
            button_color=PANEL_BG,
            button_hover_color="#242424",
            text_color=TEXT_MAIN
        ).pack(fill="x", pady=6)

        btn_row = ctk.CTkFrame(wrapper, fg_color="transparent")
        btn_row.pack(fill="x", pady=32)

        cancel_btn = ctk.CTkButton(
            btn_row,
            text="Отмена",
            fg_color=PANEL_BG,
            hover_color="#242424",
            text_color=TEXT_MUTED,
            corner_radius=12,
            width=160,
            height=44,
            command=self.show_dashboard
        )
        cancel_btn.pack(side="left")

        save_btn = ctk.CTkButton(
            btn_row,
            text="Сохранить вопрос",
            fg_color=ACCENT,
            hover_color="#0B5F5E",
            text_color="white",
            corner_radius=12,
            width=200,
            height=44,
            command=self.save_question_v2
        )
        save_btn.pack(side="right")

    def save_question_v2(self):
        QUESTIONS_FILE = Path("questions.json")

        question_text = self.q_entry.get().strip()
        if not question_text:
            messagebox.showerror("Ошибка", "Введите текст вопроса")
            return

        options = [e.get().strip() for e in self.answer_vars if e.get().strip()]
        if len(options) < 2:
            messagebox.showerror("Ошибка", "Нужно минимум 2 варианта ответа")
            return

        correct = self.correct_var.get()
        if correct >= len(options):
            messagebox.showerror("Ошибка", "Отметьте правильный вариант")
            return

        if QUESTIONS_FILE.exists():
            try:
                data = json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))
                if not isinstance(data, list):
                    data = []
            except:
                data = []
        else:
            data = []

        new_id = max([q.get("id", 0) for q in data], default=0) + 1

        new_question = {
            "id": new_id,
            "question": question_text,
            "options": options,
            "correct": correct,
            "stars": int(self.score_var.get()),
            "time": self.time_var.get(),
            "difficulty": "Легкий"
        }

        data.append(new_question)
        QUESTIONS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")

        messagebox.showinfo("Готово", "Вопрос успешно добавлен!")
        self.show_dashboard()

    # ============================================================
    # ЭКРАН УДАЛЕНИЯ ВОПРОСОВ
    # ============================================================
    def show_delete_question_screen(self):
        self.clear_content()

        wrapper = ctk.CTkFrame(self.content_frame, fg_color=PRIMARY_BG)
        wrapper.pack(fill="both", expand=True, padx=32, pady=32)

        title = ctk.CTkLabel(
            wrapper,
            text="Удалить вопрос",
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 24))

        search_row = ctk.CTkFrame(wrapper, fg_color="transparent")
        search_row.pack(fill="x", pady=(0, 20))

        self.search_var = StringVar()

        search_entry = ctk.CTkEntry(
            search_row,
            height=42,
            fg_color=PRIMARY_BG,
            border_color=BORDER_CLR,
            border_width=1,
            text_color=TEXT_MAIN,
            placeholder_text="Поиск вопроса...",
            textvariable=self.search_var
        )
        search_entry.pack(side="left", fill="x", expand=True)

        search_btn = ctk.CTkButton(
            search_row,
            text="Найти",
            fg_color=PANEL_BG,
            hover_color="#242424",
            text_color=TEXT_MUTED,
            corner_radius=10,
            width=100,
            command=self.refresh_delete_list
        )
        search_btn.pack(side="left", padx=(12, 0))

        self.list_frame = ctk.CTkScrollableFrame(
            wrapper,
            fg_color="transparent",
            width=900,
            height=550
        )
        self.list_frame.pack(fill="both", expand=True)

        self.page = 0
        self.page_size = 10

        self.refresh_delete_list()

        pag_row = ctk.CTkFrame(wrapper, fg_color="transparent")
        pag_row.pack(fill="x", pady=(16, 0))

        prev_btn = ctk.CTkButton(
            pag_row,
            text="Назад",
            fg_color=PANEL_BG,
            hover_color="#242424",
            text_color=TEXT_MUTED,
            corner_radius=10,
            width=120,
            command=self.prev_page
        )
        prev_btn.pack(side="left")

        next_btn = ctk.CTkButton(
            pag_row,
            text="Вперед",
            fg_color=PANEL_BG,
            hover_color="#242424",
            text_color=TEXT_MUTED,
            corner_radius=10,
            width=120,
            command=self.next_page
        )
        next_btn.pack(side="right")

    def refresh_delete_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        all_questions = get_all_questions()

        query = self.search_var.get().strip().lower()
        if query:
            all_questions = [
                q for q in all_questions
                if query in q.get("question", "").lower()
            ]

        start = self.page * self.page_size
        end = start + self.page_size
        page_items = all_questions[start:end]

        if not page_items:
            ctk.CTkLabel(
                self.list_frame,
                text="Ничего не найдено",
                text_color=TEXT_MUTED,
                font=ctk.CTkFont(size=16)
            ).pack(pady=20)
            return

        for q in page_items:
            card = ctk.CTkFrame(
                self.list_frame,
                fg_color=CARD_BG,
                corner_radius=12,
                border_width=1,
                border_color=BORDER_CLR
            )
            card.pack(fill="x", pady=6, padx=4)

            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=12)

            text = q.get("question", "")
            if len(text) > 120:
                text = text[:117] + "..."

            ctk.CTkLabel(
                row,
                text=text,
                text_color=TEXT_MAIN,
                font=ctk.CTkFont(size=15),
                wraplength=700,
                justify="left"
            ).pack(side="left", fill="x", expand=True)

            diff = q.get("difficulty", "Легкий").capitalize()
            diff_color = {
                "Легкий": "#4CAF50",
                "Средний": "#FFC107",
                "Сложный": "#FF5252"
            }.get(diff, "#4CAF50")

            diff_label = ctk.CTkLabel(
                row,
                text=diff,
                text_color="white",
                fg_color=diff_color,
                corner_radius=8,
                font=ctk.CTkFont(size=13),
                width=70,
                height=26
            )
            diff_label.pack(side="left", padx=12)

            del_btn = ctk.CTkButton(
                row,
                text="Удалить",
                fg_color="#FF5252",
                hover_color="#D84343",
                text_color="white",
                corner_radius=10,
                width=100,
                command=lambda qid=q["id"]: self.confirm_delete_v2(qid)
            )
            del_btn.pack(side="right")

    def next_page(self):
        self.page += 1
        self.refresh_delete_list()

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
        self.refresh_delete_list()

    def confirm_delete_v2(self, q_id):
        if messagebox.askyesno("Подтверждение", "Удалить этот вопрос?"):
            ok = delete_question(q_id)
            if ok:
                messagebox.showinfo("Готово", "Вопрос удалён")
                self.refresh_delete_list()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить вопрос")

    # ============================================================
    # ЭКРАН СПИСКА ВОПРОСОВ
    # ============================================================
    def show_question_list(self):
        self.clear_content()

        wrapper = ctk.CTkFrame(self.content_frame, fg_color=PRIMARY_BG)
        wrapper.pack(fill="both", expand=True, padx=32, pady=32)

        title = ctk.CTkLabel(
            wrapper,
            text="Список вопросов",
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 24))

        search_row = ctk.CTkFrame(wrapper, fg_color="transparent")
        search_row.pack(fill="x", pady=(0, 20))

        self.list_search_var = StringVar()

        search_entry = ctk.CTkEntry(
            search_row,
            height=42,
            fg_color=PRIMARY_BG,
            border_color=BORDER_CLR,
            border_width=1,
            text_color=TEXT_MAIN,
            placeholder_text="Поиск вопроса...",
            textvariable=self.list_search_var
        )
        search_entry.pack(side="left", fill="x", expand=True)

        search_btn = ctk.CTkButton(
            search_row,
            text="Найти",
            fg_color=PANEL_BG,
            hover_color="#242424",
            text_color=TEXT_MUTED,
            corner_radius=10,
            width=100,
            command=self.refresh_question_list
        )
        search_btn.pack(side="left", padx=(12, 0))

        self.q_list_frame = ctk.CTkScrollableFrame(
            wrapper,
            fg_color="transparent",
            width=900,
            height=550
        )
        self.q_list_frame.pack(fill="both", expand=True)

        self.q_page = 0
        self.q_page_size = 10

        self.refresh_question_list()

        pag_row = ctk.CTkFrame(wrapper, fg_color="transparent")
        pag_row.pack(fill="x", pady=(16, 0))

        prev_btn = ctk.CTkButton(
            pag_row,
            text="Назад",
            fg_color=PANEL_BG,
            hover_color="#242424",
            text_color=TEXT_MUTED,
            corner_radius=10,
            width=120,
            command=self.q_prev_page
        )
        prev_btn.pack(side="left")

        next_btn = ctk.CTkButton(
            pag_row,
            text="Вперед",
            fg_color=PANEL_BG,
            hover_color="#242424",
            text_color=TEXT_MUTED,
            corner_radius=10,
            width=120,
            command=self.q_next_page
        )
        next_btn.pack(side="right")

    def refresh_question_list(self):
        for w in self.q_list_frame.winfo_children():
            w.destroy()

        all_questions = get_all_questions()

        query = self.list_search_var.get().strip().lower()
        if query:
            all_questions = [
                q for q in all_questions
                if query in q.get("question", "").lower()
            ]

        start = self.q_page * self.q_page_size
        end = start + self.q_page_size
        page_items = all_questions[start:end]

        if not page_items:
            ctk.CTkLabel(
                self.q_list_frame,
                text="Ничего не найдено",
                text_color=TEXT_MUTED,
                font=ctk.CTkFont(size=16)
            ).pack(pady=20)
            return

        for q in page_items:
            card = ctk.CTkFrame(
                self.q_list_frame,
                fg_color=CARD_BG,
                corner_radius=12,
                border_width=1,
                border_color=BORDER_CLR
            )
            card.pack(fill="x", pady=6, padx=4)

            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=12)

            text = q.get("question", "")
            if len(text) > 120:
                text = text[:117] + "..."

            ctk.CTkLabel(
                row,
                text=text,
                text_color=TEXT_MAIN,
                font=ctk.CTkFont(size=15),
                wraplength=700,
                justify="left"
            ).pack(side="left", fill="x", expand=True)

            diff = q.get("difficulty", "Легкий").capitalize()
            diff_color = {
                "Легкий": "#4CAF50",
                "Средний": "#FFC107",
                "Сложный": "#FF5252"
            }.get(diff, "#4CAF50")

            diff_label = ctk.CTkLabel(
                row,
                text=diff,
                text_color="white",
                fg_color=diff_color,
                corner_radius=8,
                font=ctk.CTkFont(size=13),
                width=70,
                height=26
            )
            diff_label.pack(side="right", padx=12)

    def q_next_page(self):
        self.q_page += 1
        self.refresh_question_list()

    def q_prev_page(self):
        if self.q_page > 0:
            self.q_page -= 1
        self.refresh_question_list()

    # ============================================================
    # ЭКРАН ИГРЫ
    # ============================================================
    def start_quiz_screen(self):
        self.clear_content()

        wrapper = ctk.CTkFrame(self.content_frame, fg_color=PRIMARY_BG)
        wrapper.pack(fill="both", expand=True, padx=32, pady=32)

        title = ctk.CTkLabel(
            wrapper,
            text="Игра",
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 24))

        status_row = ctk.CTkFrame(wrapper, fg_color="transparent")
        status_row.pack(fill="x", pady=(0, 24))

        def make_status_card(parent, title, value):
            card = ctk.CTkFrame(
                parent,
                fg_color=CARD_BG,
                corner_radius=14,
                border_width=1,
                border_color=BORDER_CLR,
                height=90
            )
            card.pack(side="left", fill="x", expand=True, padx=8)

            ctk.CTkLabel(
                card,
                text=title,
                text_color=TEXT_MUTED,
                font=ctk.CTkFont(size=15)
            ).pack(anchor="w", padx=20, pady=(12, 2))

            lbl = ctk.CTkLabel(
                card,
                text=value,
                text_color=TEXT_MAIN,
                font=ctk.CTkFont(size=28, weight="bold")
            )
            lbl.pack(anchor="w", padx=20)

            return lbl

        self.stars_label = make_status_card(status_row, "Звёзды", str(self.progress["total_stars"]))
        self.lives_label = make_status_card(status_row, "Жизни", str(self.progress["lives"]))

        self.fretboard = ctk.CTkCanvas(
            wrapper,
            width=1100,
            height=260,
            bg="#2A1E14",
            highlightthickness=0
        )
        self.fretboard.pack(pady=(0, 24))

        self.draw_fretboard_v2()

        self.quiz_question_label = ctk.CTkLabel(
            wrapper,
            text="",
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(size=22),
            wraplength=1000,
            justify="center"
        )
        self.quiz_question_label.pack(pady=(0, 24))

        self.answer_buttons = []

        for i in range(4):
            btn = ctk.CTkButton(
                wrapper,
                text=f"Вариант {i+1}",
                fg_color=CARD_BG,
                hover_color="#242424",
                text_color=TEXT_MAIN,
                corner_radius=12,
                height=52,
                width=600,
                font=ctk.CTkFont(size=18),
                command=lambda idx=i: self.check_answer_v2(idx)
            )
            btn.pack(pady=8)
            self.answer_buttons.append(btn)

        back_btn = ctk.CTkButton(
            wrapper,
            text="Вернуться в меню",
            fg_color=PANEL_BG,
            hover_color="#242424",
            text_color=TEXT_MUTED,
            corner_radius=12,
            height=44,
            width=200,
            command=self.show_dashboard
        )
        back_btn.pack(pady=24)

        self.current_question = None
        self.load_next_question_v2()

    def draw_fretboard_v2(self):
        w = 1100
        h = 260
        fret_count = 12

        self.fret_w = w / fret_count
        self.fret_h = h / 6

        for f in range(fret_count + 1):
            x = f * self.fret_w
            self.fretboard.create_line(
                x, 0, x, h,
                fill="#CFCFCF",
                width=3
            )

        for s in range(6):
            y = (s + 0.5) * self.fret_h
            thickness = 1 + s * 0.5
            self.fretboard.create_line(
                0, y, w, y,
                fill="#D0D0D0",
                width=thickness
            )

        for f in [3, 5, 7, 9, 12]:
            x = (f - 0.5) * self.fret_w
            y = h / 2
            r = 8

            if f == 12:
                self.fretboard.create_oval(x - 20, y - r, x - 4, y + r, fill="white", outline="")
                self.fretboard.create_oval(x + 4, y - r, x + 20, y + r, fill="white", outline="")
            else:
                self.fretboard.create_oval(x - r, y - r, x + r, y + r, fill="white", outline="")

    def highlight_note_v2(self, string, fret, color):
        if string is None or fret is None:
            return

        s = string - 1
        f = fret

        x = f * self.fret_w + self.fret_w / 2
        y = s * self.fret_h + self.fret_h / 2

        r = 14
        self.fretboard.create_oval(
            x - r, y - r,
            x + r, y + r,
            fill=color,
            outline=""
        )

    def load_next_question_v2(self):
        q = get_random_question()
        if not q:
            self.quiz_question_label.configure(text="Вопросы закончились!")
            for btn in self.answer_buttons:
                btn.configure(state="disabled")
            return

        self.current_question = q
        self.quiz_question_label.configure(text=q["question"])

        for i, btn in enumerate(self.answer_buttons):
            btn.configure(
                text=q["options"][i],
                fg_color=CARD_BG,
                state="normal"
            )

        self.fretboard.delete("all")
        self.draw_fretboard_v2()

    def check_answer_v2(self, idx):
        correct = self.current_question["correct"]

        if idx == correct:
            self.highlight_note_v2(self.current_question.get("string"),
                                   self.current_question.get("fret"),
                                   "#4CAF50")
        else:
            self.highlight_note_v2(self.current_question.get("string"),
                                   self.current_question.get("fret"),
                                   "#FF5252")

        if idx == correct:
            self.progress["total_stars"] += self.current_question.get("stars", 10)
            self.progress["correct_answers"] += 1
        else:
            self.progress["lives"] -= 1
            self.progress["wrong_answers"].append(self.current_question)

        self.stars_label.configure(text=str(self.progress["total_stars"]))
        self.lives_label.configure(text=str(self.progress["lives"]))

        for btn in self.answer_buttons:
            btn.configure(state="disabled")

        if self.progress["lives"] <= 0:
            messagebox.showinfo("Игра окончена", "У тебя закончились жизни")
            self.show_dashboard()
            return

        self.after(700, self.load_next_question_v2)

    # ============================================================
    # ВЫХОД
    # ============================================================
    def quit_app(self):
        save_progress(self.progress)
        self.destroy()
        sys.exit(0)


# ============================================================
# Точка входа
# ============================================================
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    app = GuitarQuizAppV2()
    app.mainloop()

