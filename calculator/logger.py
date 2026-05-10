"""
파일명: logger.py
파일 목적: 계산기 프로그램 실행 로그 관리 모듈
작성일: 2026-05-10
버전: 1.0.0
"""

import logging
import os
from datetime import datetime


def setup_logger(log_dir: str = None) -> logging.Logger:
    """
    로거를 설정하고 반환합니다.
    콘솔과 log.txt 파일 양쪽에 동시에 출력합니다.

    Args:
        log_dir (str): 로그 파일을 저장할 디렉토리 경로 (None이면 현재 디렉토리)

    Returns:
        logging.Logger: 설정된 로거 인스턴스
    """
    logger = logging.getLogger("Calculator")
    logger.setLevel(logging.DEBUG)

    # 중복 핸들러 방지
    if logger.handlers:
        logger.handlers.clear()

    # 로그 포맷 설정 (타임스탬프 포함)
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # ── 콘솔 핸들러 ──
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ── 파일 핸들러 (log.txt) ──
    if log_dir is None:
        log_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(log_dir, "..")   # 프로젝트 루트

    log_path = os.path.join(os.path.abspath(log_dir), "log.txt")

    try:
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"로그 파일 생성 실패: {e}")

    return logger


class CalcLogger:
    """
    계산기 전용 로그 래퍼 클래스.
    계산 이벤트, 오류, 실행 상태를 구조화하여 기록합니다.
    """

    def __init__(self, log_dir: str = None):
        """
        CalcLogger 초기화.

        Args:
            log_dir (str): 로그 파일 저장 경로
        """
        self.logger = setup_logger(log_dir)
        self.session_start = datetime.now()
        self.logger.info("=" * 55)
        self.logger.info("  계산기 프로그램 시작")
        self.logger.info(f"  세션 시작 시각: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 55)

    def log_start(self):
        """프로그램 GUI 시작을 기록합니다."""
        self.logger.info("GUI 윈도우가 초기화되었습니다.")

    def log_button(self, label: str):
        """
        버튼 클릭 이벤트를 기록합니다.

        Args:
            label (str): 클릭된 버튼 레이블
        """
        self.logger.debug(f"버튼 클릭: [{label}]")

    def log_calculation(self, expression: str, result: str):
        """
        계산 결과를 기록합니다.

        Args:
            expression (str): 수식 문자열
            result (str): 계산 결과
        """
        self.logger.info(f"계산 완료 → {expression} {result}")

    def log_error(self, message: str):
        """
        오류 내용을 기록합니다.

        Args:
            message (str): 오류 메시지
        """
        self.logger.error(f"오류 발생: {message}")

    def log_reset(self):
        """초기화(C/CE) 이벤트를 기록합니다."""
        self.logger.info("계산기 초기화 (리셋)")

    def log_close(self):
        """프로그램 종료를 기록합니다."""
        elapsed = datetime.now() - self.session_start
        total_sec = int(elapsed.total_seconds())
        self.logger.info("=" * 55)
        self.logger.info(f"  계산기 프로그램 종료 (사용 시간: {total_sec}초)")
        self.logger.info("=" * 55)
