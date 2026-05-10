"""
파일명: calculator_gui.py
파일 목적: 계산기 GUI 화면 구성 및 이벤트 처리 모듈
작성일: 2026-05-10
버전: 1.0.0
"""

import tkinter as tk
from tkinter import font as tkfont
from calculator.calculator_engine import CalculatorEngine
from calculator.logger import CalcLogger


# ── 색상 팔레트 상수 ──────────────────────────────────────────
COLORS = {
    "bg":           "#1C1C1E",   # 전체 배경 (다크 그레이)
    "display_bg":   "#1C1C1E",   # 디스플레이 배경
    "expr_fg":      "#8E8E93",   # 수식 표시 글자색 (연한 회색)
    "main_fg":      "#FFFFFF",   # 메인 숫자 글자색
    "btn_func":     "#2C2C2E",   # 기능 버튼 배경 (AC, +/-, %)
    "btn_func_fg":  "#FFFFFF",   # 기능 버튼 글자색
    "btn_op":       "#FF9F0A",   # 연산자 버튼 배경 (오렌지)
    "btn_op_fg":    "#FFFFFF",   # 연산자 버튼 글자색
    "btn_op_act":   "#FFFFFF",   # 연산자 활성화 배경 (흰색)
    "btn_op_act_fg":"#FF9F0A",   # 연산자 활성화 글자색
    "btn_num":      "#3A3A3C",   # 숫자 버튼 배경
    "btn_num_fg":   "#FFFFFF",   # 숫자 버튼 글자색
    "btn_zero":     "#3A3A3C",   # 0 버튼 배경 (와이드)
    "btn_hover_dark":"#505052",  # 어두운 버튼 호버
    "btn_hover_op": "#FFB340",   # 연산자 버튼 호버
    "btn_hover_func":"#48484A",  # 기능 버튼 호버
    "btn_press":    "#636366",   # 버튼 눌림 효과
}

# ── 버튼 레이아웃 정의 ────────────────────────────────────────
# 각 튜플: (레이블, 버튼 타입, 열span)
# 버튼 타입: "func"=기능, "op"=연산자, "num"=숫자, "zero"=넓은 0
BUTTON_LAYOUT = [
    [("AC",  "func", 1), ("+/-", "func", 1), ("%",  "func", 1), ("÷",  "op", 1)],
    [("7",   "num",  1), ("8",   "num",  1), ("9",  "num",  1), ("×",  "op", 1)],
    [("4",   "num",  1), ("5",   "num",  1), ("6",  "num",  1), ("-",  "op", 1)],
    [("1",   "num",  1), ("2",   "num",  1), ("3",  "num",  1), ("+",  "op", 1)],
    [("0",   "zero", 2), (".",   "num",  1), ("=",  "op", 1)],
]


class CalculatorGUI:
    """
    계산기 GUI 메인 클래스.
    tkinter를 사용하여 실제 계산기와 유사한 UI를 구성합니다.
    """

    def __init__(self, root: tk.Tk, calc_logger: CalcLogger):
        """
        GUI 초기화.

        Args:
            root (tk.Tk): tkinter 루트 윈도우
            calc_logger (CalcLogger): 로그 기록 객체
        """
        self.root = root
        self.logger = calc_logger
        self.engine = CalculatorEngine()

        # 현재 활성화된 연산자 버튼 추적 (강조 표시용)
        self.active_op_btn = None
        self.buttons = {}   # 레이블 → 버튼 위젯 매핑

        self._setup_window()
        self._setup_display()
        self._setup_buttons()
        self._bind_keyboard()

        self.logger.log_start()

    # ── 윈도우 설정 ────────────────────────────────────────────

    def _setup_window(self):
        """윈도우 크기, 제목, 배경 등 기본 설정"""
        self.root.title("계산기")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(False, False)

        # 화면 중앙에 창 배치
        win_w, win_h = 380, 580
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - win_w) // 2
        y = (screen_h - win_h) // 2
        self.root.geometry(f"{win_w}x{win_h}+{x}+{y}")

        # 종료 이벤트 바인딩
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── 디스플레이 영역 설정 ──────────────────────────────────

    def _setup_display(self):
        """상단 디스플레이 영역 구성 (수식 + 메인 숫자)"""
        display_frame = tk.Frame(
            self.root,
            bg=COLORS["display_bg"],
            padx=20,
            pady=10
        )
        display_frame.pack(fill=tk.X)

        # ── 수식 표시 라벨 (상단, 작은 글씨) ──
        self.expr_var = tk.StringVar(value="")
        self.expr_label = tk.Label(
            display_frame,
            textvariable=self.expr_var,
            font=("SF Pro Display", 18, "normal"),
            bg=COLORS["display_bg"],
            fg=COLORS["expr_fg"],
            anchor="e",         # 오른쪽 정렬
            height=1
        )
        self.expr_label.pack(fill=tk.X, pady=(10, 0))

        # ── 메인 숫자 표시 라벨 (하단, 큰 글씨) ──
        self.main_var = tk.StringVar(value="0")
        self.main_label = tk.Label(
            display_frame,
            textvariable=self.main_var,
            font=("SF Pro Display", 64, "normal"),
            bg=COLORS["display_bg"],
            fg=COLORS["main_fg"],
            anchor="e",         # 오른쪽 정렬
            height=1
        )
        self.main_label.pack(fill=tk.X, pady=(0, 15))

    # ── 버튼 영역 설정 ────────────────────────────────────────

    def _setup_buttons(self):
        """버튼 그리드 구성"""
        btn_frame = tk.Frame(self.root, bg=COLORS["bg"], padx=10, pady=5)
        btn_frame.pack(fill=tk.BOTH, expand=True)

        # 4열 균등 배치를 위한 열 가중치 설정
        for col in range(4):
            btn_frame.columnconfigure(col, weight=1)

        for row_idx, row_def in enumerate(BUTTON_LAYOUT):
            btn_frame.rowconfigure(row_idx, weight=1)
            col_idx = 0
            for (label, btn_type, col_span) in row_def:
                btn = self._create_button(btn_frame, label, btn_type)
                btn.grid(
                    row=row_idx,
                    column=col_idx,
                    columnspan=col_span,
                    padx=5,
                    pady=5,
                    sticky="nsew"
                )
                self.buttons[label] = btn
                col_idx += col_span

    def _create_button(self, parent, label: str, btn_type: str) -> tk.Button:
        """
        개별 버튼 위젯을 생성합니다.

        Args:
            parent: 부모 프레임
            label (str): 버튼 레이블
            btn_type (str): 버튼 타입 ("func" / "op" / "num" / "zero")

        Returns:
            tk.Button: 생성된 버튼 위젯
        """
        # 타입별 색상 결정
        if btn_type == "func":
            bg  = COLORS["btn_func"]
            fg  = COLORS["btn_func_fg"]
            hover_bg = COLORS["btn_hover_func"]
        elif btn_type == "op":
            bg  = COLORS["btn_op"]
            fg  = COLORS["btn_op_fg"]
            hover_bg = COLORS["btn_hover_op"]
        else:   # "num" / "zero"
            bg  = COLORS["btn_num"]
            fg  = COLORS["btn_num_fg"]
            hover_bg = COLORS["btn_hover_dark"]

        btn = tk.Button(
            parent,
            text=label,
            font=("SF Pro Display", 26, "normal"),
            bg=bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground=fg,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            command=lambda l=label: self._on_button_click(l)
        )

        # ── 호버 효과 바인딩 ──
        btn.bind("<Enter>",  lambda e, b=btn, hbg=hover_bg: b.configure(bg=hbg))
        btn.bind("<Leave>",  lambda e, b=btn, obg=bg: b.configure(bg=obg))
        btn.bind("<ButtonPress-1>",   lambda e, b=btn: b.configure(bg=COLORS["btn_press"]))
        btn.bind("<ButtonRelease-1>", lambda e, b=btn, hbg=hover_bg: b.configure(bg=hbg))

        # 둥근 모서리 효과 (패딩으로 대체)
        btn.configure(padx=5, pady=5)

        return btn

    # ── 버튼 클릭 처리 ────────────────────────────────────────

    def _on_button_click(self, label: str):
        """
        버튼 클릭 이벤트 통합 핸들러.

        Args:
            label (str): 클릭된 버튼 레이블
        """
        self.logger.log_button(label)

        if label == "AC":
            self._handle_clear()
        elif label == "+/-":
            self._handle_toggle_sign()
        elif label == "%":
            self._handle_percent()
        elif label in ("+", "-", "×", "÷"):
            self._handle_operator(label)
        elif label == "=":
            self._handle_equals()
        elif label == ".":
            self._handle_digit(".")
        else:
            # 숫자 버튼 (0~9)
            self._handle_digit(label)

    def _handle_clear(self):
        """AC 버튼: 전체 초기화"""
        self.engine.reset()
        self._reset_op_highlight()
        self.expr_var.set("")
        self.main_var.set("0")
        self._update_display_font("0")
        self.logger.log_reset()

    def _handle_digit(self, digit: str):
        """숫자 / 소수점 입력 처리"""
        result = self.engine.input_digit(digit)
        self._reset_op_highlight()
        self.main_var.set(self._add_commas(result))
        self._update_display_font(result)

    def _handle_operator(self, op: str):
        """연산자 버튼 입력 처리"""
        expr = self.engine.input_operator(op)
        self.expr_var.set(expr)
        # 현재 연산자 버튼 강조 표시
        self._highlight_op_button(op)

    def _handle_equals(self):
        """= 버튼: 최종 결과 계산"""
        result_str, expr_str = self.engine.calculate_result()
        self._reset_op_highlight()
        self.expr_var.set(expr_str)
        display_val = self._add_commas(result_str)
        self.main_var.set(display_val)
        self._update_display_font(result_str)

        if result_str != "오류":
            self.logger.log_calculation(expr_str, result_str)
        else:
            self.logger.log_error("0으로 나누기 또는 잘못된 입력")

    def _handle_toggle_sign(self):
        """부호 전환 (+/-) 처리"""
        result = self.engine.toggle_sign()
        self.main_var.set(self._add_commas(result))
        self._update_display_font(result)

    def _handle_percent(self):
        """퍼센트 (%) 처리"""
        result = self.engine.input_percent()
        self.main_var.set(self._add_commas(result))
        self._update_display_font(result)

    # ── 연산자 버튼 강조 표시 ─────────────────────────────────

    def _highlight_op_button(self, op: str):
        """
        선택된 연산자 버튼을 흰색 배경 + 오렌지 글씨로 강조합니다.

        Args:
            op (str): 강조할 연산자 문자
        """
        # 이전 강조 해제
        self._reset_op_highlight()

        if op in self.buttons:
            btn = self.buttons[op]
            btn.configure(
                bg=COLORS["btn_op_act"],
                fg=COLORS["btn_op_act_fg"]
            )
            # 호버 효과도 업데이트
            btn.bind("<Enter>",  lambda e, b=btn: b.configure(bg="#E0E0E0"))
            btn.bind("<Leave>",  lambda e, b=btn: b.configure(
                bg=COLORS["btn_op_act"], fg=COLORS["btn_op_act_fg"]))
            self.active_op_btn = op

    def _reset_op_highlight(self):
        """활성화된 연산자 버튼의 강조를 원래 색으로 복구합니다."""
        if self.active_op_btn and self.active_op_btn in self.buttons:
            btn = self.buttons[self.active_op_btn]
            btn.configure(
                bg=COLORS["btn_op"],
                fg=COLORS["btn_op_fg"]
            )
            # 호버 효과 복구
            btn.bind("<Enter>",  lambda e, b=btn: b.configure(bg=COLORS["btn_hover_op"]))
            btn.bind("<Leave>",  lambda e, b=btn: b.configure(bg=COLORS["btn_op"]))
        self.active_op_btn = None

    # ── 디스플레이 보조 기능 ──────────────────────────────────

    def _add_commas(self, value: str) -> str:
        """
        숫자 문자열에 천 단위 쉼표를 추가합니다.
        소수점 이하는 쉼표 없이 그대로 유지합니다.

        Args:
            value (str): 원본 숫자 문자열

        Returns:
            str: 쉼표가 적용된 문자열
        """
        if value in ("오류", ""):
            return value

        try:
            negative = value.startswith("-")
            abs_val = value.lstrip("-")

            if "." in abs_val:
                integer_part, decimal_part = abs_val.split(".", 1)
            else:
                integer_part, decimal_part = abs_val, None

            # 천 단위 쉼표 적용
            formatted = f"{int(integer_part):,}" if integer_part else "0"

            result = f"{formatted}.{decimal_part}" if decimal_part is not None else formatted
            return f"-{result}" if negative else result

        except (ValueError, Exception):
            return value

    def _update_display_font(self, value: str):
        """
        표시되는 숫자 길이에 따라 폰트 크기를 동적으로 조절합니다.

        Args:
            value (str): 현재 표시 중인 값 문자열
        """
        length = len(self._add_commas(value))

        if length <= 9:
            size = 64
        elif length <= 12:
            size = 48
        elif length <= 15:
            size = 36
        else:
            size = 28

        self.main_label.configure(font=("SF Pro Display", size, "normal"))

    # ── 키보드 바인딩 ─────────────────────────────────────────

    def _bind_keyboard(self):
        """키보드 입력을 버튼 클릭으로 연결합니다."""
        # 숫자 키 (일반 + 숫자패드)
        for digit in "0123456789":
            self.root.bind(digit, lambda e, d=digit: self._on_button_click(d))
            self.root.bind(f"<KP_{digit}>", lambda e, d=digit: self._on_button_click(d))

        # 연산자 키
        self.root.bind("+",         lambda e: self._on_button_click("+"))
        self.root.bind("-",         lambda e: self._on_button_click("-"))
        self.root.bind("*",         lambda e: self._on_button_click("×"))
        self.root.bind("/",         lambda e: self._on_button_click("÷"))
        self.root.bind("<KP_Add>",      lambda e: self._on_button_click("+"))
        self.root.bind("<KP_Subtract>", lambda e: self._on_button_click("-"))
        self.root.bind("<KP_Multiply>", lambda e: self._on_button_click("×"))
        self.root.bind("<KP_Divide>",   lambda e: self._on_button_click("÷"))

        # 결과 및 기타
        self.root.bind("<Return>",      lambda e: self._on_button_click("="))
        self.root.bind("<KP_Enter>",    lambda e: self._on_button_click("="))
        self.root.bind(".",             lambda e: self._on_button_click("."))
        self.root.bind("<KP_Decimal>",  lambda e: self._on_button_click("."))
        self.root.bind("%",             lambda e: self._on_button_click("%"))
        self.root.bind("<BackSpace>",   lambda e: self._handle_backspace())
        self.root.bind("<Escape>",      lambda e: self._on_button_click("AC"))
        self.root.bind("c",             lambda e: self._on_button_click("AC"))
        self.root.bind("C",             lambda e: self._on_button_click("AC"))

    def _handle_backspace(self):
        """백스페이스 키: 마지막 입력 삭제"""
        self.logger.log_button("⌫ (Backspace)")
        result = self.engine.backspace()
        self.main_var.set(self._add_commas(result))
        self._update_display_font(result)

    # ── 종료 처리 ─────────────────────────────────────────────

    def _on_close(self):
        """윈도우 닫기 버튼 클릭 시 종료 처리"""
        self.logger.log_close()
        self.root.destroy()
