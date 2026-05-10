"""
파일명: calculator_engine.py
파일 목적: 계산기 핵심 연산 로직 처리 모듈
작성일: 2026-05-10
버전: 1.0.0
"""

from decimal import Decimal, InvalidOperation, getcontext

# 소수점 정밀도 설정 (최대 28자리)
getcontext().prec = 28


class CalculatorEngine:
    """
    계산기 핵심 연산 엔진 클래스.
    사칙연산, 퍼센트, 부호 전환 등의 기본 기능을 처리합니다.
    """

    def __init__(self):
        """계산기 엔진 초기화 - 모든 상태를 초기값으로 설정"""
        self.reset()

    def reset(self):
        """
        모든 계산 상태를 초기화합니다.
        - current_value: 현재 입력 중인 값 (문자열)
        - stored_value: 이전 피연산자 (Decimal)
        - operator: 현재 선택된 연산자
        - result: 최종 계산 결과
        - new_input: 새 숫자 입력 시작 여부
        - error: 오류 발생 여부
        """
        self.current_value: str = "0"
        self.stored_value: Decimal = Decimal("0")
        self.operator: str = ""
        self.result: str = "0"
        self.new_input: bool = True
        self.error: bool = False
        self.history: list = []         # 계산 히스토리 저장
        self.expression: str = ""       # 수식 문자열 (상단 표시용)

    def input_digit(self, digit: str) -> str:
        """
        숫자 또는 소수점 입력 처리.

        Args:
            digit (str): 입력된 숫자 문자 ('0'~'9' 또는 '.')

        Returns:
            str: 현재 디스플레이에 표시할 값
        """
        try:
            # 오류 상태이면 초기화 후 입력
            if self.error:
                self.reset()

            if self.new_input:
                # 새 입력 시작: 소수점이면 '0.'으로, 아니면 해당 숫자로 시작
                self.current_value = "0." if digit == "." else digit
                self.new_input = False
            else:
                # 소수점 중복 방지
                if digit == "." and "." in self.current_value:
                    return self.current_value

                # 최대 15자리까지만 입력 허용 (소수점 포함하지 않고 계산)
                digits_only = self.current_value.replace(".", "").replace("-", "")
                if len(digits_only) >= 15 and digit != ".":
                    return self.current_value

                # 초기 '0' 상태에서 숫자 입력 시 '0' 대체
                if self.current_value == "0" and digit != ".":
                    self.current_value = digit
                else:
                    self.current_value += digit

            return self.current_value

        except Exception as e:
            self.error = True
            return "오류"

    def input_operator(self, op: str) -> str:
        """
        연산자 입력 처리.

        Args:
            op (str): 연산자 문자 ('+', '-', '×', '÷')

        Returns:
            str: 수식 표시용 문자열
        """
        try:
            if self.error:
                self.reset()
                return ""

            current = Decimal(self.current_value)

            # 이미 연산자가 있고 새 숫자 입력이 없는 경우 → 연산자만 교체
            if self.operator and self.new_input:
                self.operator = op
                # 수식 표시에서 마지막 연산자 교체
                if self.expression:
                    self.expression = self.expression[:-2] + f" {op}"
                return self.expression

            # 이전 연산자가 있으면 연속 계산 수행
            if self.operator and not self.new_input:
                result = self._calculate(self.stored_value, current, self.operator)
                if result is None:
                    return self.expression
                self.stored_value = result
                self.current_value = self._format_number(result)
                self.expression = f"{self._format_number(result)} {op}"
            else:
                # 첫 번째 피연산자 저장
                self.stored_value = current
                self.expression = f"{self._format_number(current)} {op}"

            self.operator = op
            self.new_input = True

            return self.expression

        except (InvalidOperation, Exception) as e:
            self.error = True
            self.current_value = "오류"
            return "오류"

    def calculate_result(self) -> tuple:
        """
        '=' 버튼 입력 시 최종 결과 계산.

        Returns:
            tuple: (결과값 문자열, 수식 문자열)
        """
        try:
            if self.error:
                self.reset()
                return ("0", "")

            if not self.operator:
                # 연산자 없이 '=' 눌렀을 때는 현재 값 그대로 반환
                return (self.current_value, "")

            current = Decimal(self.current_value)
            full_expression = f"{self.expression} {self._format_number(current)} ="

            result = self._calculate(self.stored_value, current, self.operator)
            if result is None:
                return (self.current_value, full_expression)

            result_str = self._format_number(result)

            # 히스토리에 계산 기록 저장
            self.history.append({
                "expression": full_expression,
                "result": result_str
            })

            # 결과를 다음 연산의 첫 번째 피연산자로 설정
            self.stored_value = result
            self.current_value = result_str
            self.operator = ""
            self.expression = ""
            self.new_input = True

            return (result_str, full_expression)

        except (InvalidOperation, Exception) as e:
            self.error = True
            self.current_value = "오류"
            return ("오류", "")

    def _calculate(self, a: Decimal, b: Decimal, op: str):
        """
        실제 연산 수행 내부 메서드.

        Args:
            a (Decimal): 첫 번째 피연산자
            b (Decimal): 두 번째 피연산자
            op (str): 연산자

        Returns:
            Decimal 또는 None (오류 시)
        """
        try:
            if op == "+":
                return a + b
            elif op == "-":
                return a - b
            elif op == "×":
                return a * b
            elif op == "÷":
                if b == 0:
                    # 0으로 나누기 처리
                    self.error = True
                    self.current_value = "오류"
                    return None
                return a / b
            else:
                return b
        except (InvalidOperation, Exception):
            self.error = True
            self.current_value = "오류"
            return None

    def toggle_sign(self) -> str:
        """
        현재 값의 부호를 전환합니다 (양수 ↔ 음수).

        Returns:
            str: 부호 전환된 값 문자열
        """
        try:
            if self.error or self.current_value in ("0", "오류"):
                return self.current_value

            value = Decimal(self.current_value)
            value = -value
            self.current_value = self._format_number(value)
            return self.current_value

        except (InvalidOperation, Exception):
            return self.current_value

    def input_percent(self) -> str:
        """
        현재 값을 퍼센트로 변환합니다 (÷ 100).

        Returns:
            str: 퍼센트 변환된 값 문자열
        """
        try:
            if self.error or self.current_value == "오류":
                return self.current_value

            value = Decimal(self.current_value)
            value = value / Decimal("100")
            self.current_value = self._format_number(value)
            return self.current_value

        except (InvalidOperation, Exception):
            return self.current_value

    def backspace(self) -> str:
        """
        마지막 입력 문자를 삭제합니다.

        Returns:
            str: 삭제 후 현재 값 문자열
        """
        try:
            if self.error or self.new_input:
                self.reset()
                return "0"

            if len(self.current_value) <= 1:
                # 한 자리 남았으면 '0'으로 초기화
                self.current_value = "0"
            elif self.current_value == "-0" or (
                len(self.current_value) == 2 and self.current_value[0] == "-"
            ):
                self.current_value = "0"
            else:
                self.current_value = self.current_value[:-1]
                # 소수점만 남은 경우 처리 (예: "3.")
                if self.current_value.endswith("."):
                    self.current_value = self.current_value[:-1]
                # 부호만 남은 경우 처리
                if self.current_value in ("-", ""):
                    self.current_value = "0"

            return self.current_value

        except Exception:
            self.reset()
            return "0"

    def _format_number(self, value: Decimal) -> str:
        """
        Decimal 값을 디스플레이용 문자열로 변환합니다.
        불필요한 소수점 이하 0을 제거하고, 정수는 정수 형태로 출력합니다.

        Args:
            value (Decimal): 변환할 숫자

        Returns:
            str: 형식화된 숫자 문자열
        """
        try:
            # 정규화하여 불필요한 0 제거
            normalized = value.normalize()
            formatted = str(normalized)

            # 지수 표기법(E)이 포함된 경우 처리
            if "E" in formatted or "e" in formatted:
                # 매우 크거나 작은 수는 지수 표기 유지
                return formatted

            # 정수인 경우 소수점 제거
            if "." in formatted:
                formatted = formatted.rstrip("0").rstrip(".")

            return formatted

        except Exception:
            return str(value)

    def get_history(self) -> list:
        """
        계산 히스토리를 반환합니다.

        Returns:
            list: 계산 기록 딕셔너리 리스트
        """
        return self.history.copy()
