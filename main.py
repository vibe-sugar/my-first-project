"""
파일명: main.py
파일 목적: 계산기 프로그램 메인 실행 진입점
작성일: 2026-05-10
버전: 1.0.0
"""

import tkinter as tk
import sys
import os

# 프로젝트 루트를 sys.path에 추가 (패키지 임포트 보장)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calculator.calculator_gui import CalculatorGUI
from calculator.logger import CalcLogger


def main():
    """
    계산기 프로그램 메인 함수.
    tkinter 루트 윈도우를 생성하고 GUI를 초기화한 뒤 이벤트 루프를 실행합니다.
    """
    # 로거 초기화 (log.txt 생성)
    log_dir = os.path.dirname(os.path.abspath(__file__))
    calc_logger = CalcLogger(log_dir=log_dir)

    try:
        calc_logger.logger.info("tkinter 루트 윈도우 생성 중...")

        # tkinter 루트 윈도우 생성
        root = tk.Tk()

        calc_logger.logger.info("CalculatorGUI 초기화 중...")

        # GUI 초기화
        app = CalculatorGUI(root, calc_logger)

        calc_logger.logger.info("계산기 GUI 실행 완료 - 이벤트 루프 시작")
        print("\n" + "=" * 45)
        print("  계산기 프로그램이 실행되었습니다.")
        print("  창을 닫으면 프로그램이 종료됩니다.")
        print("  키보드 단축키도 지원합니다!")
        print("=" * 45 + "\n")

        # 이벤트 루프 시작 (창이 닫힐 때까지 실행)
        root.mainloop()

        calc_logger.logger.info("이벤트 루프 종료 - 프로그램 정상 종료")

    except tk.TclError as e:
        # tkinter 관련 오류 (디스플레이 없음 등)
        calc_logger.log_error(f"tkinter 오류: {e}")
        print(f"\n[오류] tkinter 초기화 실패: {e}")
        print("디스플레이 환경이 필요합니다. (GUI 지원 환경에서 실행해주세요)")
        sys.exit(1)

    except Exception as e:
        # 그 외 예상치 못한 오류
        calc_logger.log_error(f"예상치 못한 오류: {e}")
        print(f"\n[오류] 프로그램 실행 중 오류가 발생했습니다: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
