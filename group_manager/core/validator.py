"""
验证器模块

负责验证加群申请，支持正则表达式、关键词、白名单和黑名单。
"""

import re
from typing import List, Dict, Tuple, Optional
from enum import Enum


class RuleType(Enum):
    """规则类型枚举"""
    KEYWORD = "keyword"
    REGEX = "regex"


class ValidationResult(Enum):
    """验证结果枚举"""
    ALLOW = "allow"
    REJECT = "reject"
    WHITELISTED = "whitelisted"
    BLACKLISTED = "blacklisted"


class Validator:
    """验证器类"""

    def __init__(self):
        """初始化验证器"""
        pass

    @staticmethod
    def is_regex_pattern(pattern: str) -> bool:
        """
        判断是否为正则表达式模式

        Args:
            pattern: 待判断的模式字符串

        Returns:
            如果是正则表达式模式返回 True，否则返回 False
        """
        return pattern.startswith("/") and pattern.endswith("/") and len(pattern) > 2

    @staticmethod
    def validate_regex(pattern: str) -> Tuple[bool, Optional[str]]:
        """
        验证正则表达式是否有效

        Args:
            pattern: 正则表达式（不包含 // 包裹）

        Returns:
            (是否有效, 错误信息)
        """
        try:
            re.compile(pattern)
            return True, None
        except re.error as e:
            return False, str(e)

    async def validate_request(
        self,
        group_id: str,
        user_id: str,
        request_text: str,
        rules: List[Dict],
        whitelist: List[str],
        blacklist: List[str],
        default_mode: str = "allow"
    ) -> Tuple[ValidationResult, List[Dict]]:
        """
        验证加群申请

        Args:
            group_id: 群ID
            user_id: 用户ID
            request_text: 申请文本
            rules: 规则列表
            whitelist: 白名单列表
            blacklist: 黑名单列表
            default_mode: 默认模式（"allow" 或 "reject"）

        Returns:
            (验证结果, 匹配的规则列表)
        """
        # 1. 首先检查黑名单
        if user_id in blacklist:
            return ValidationResult.BLACKLISTED, []

        # 2. 然后检查白名单
        if user_id in whitelist:
            return ValidationResult.WHITELISTED, []

        # 3. 如果没有规则，使用默认模式
        if not rules:
            if default_mode == "allow":
                return ValidationResult.ALLOW, []
            else:
                return ValidationResult.REJECT, []

        # 4. 检查规则匹配
        matched_rules = []

        for rule in rules:
            if rule["type"] == RuleType.REGEX.value:
                try:
                    if re.search(rule["content"], request_text):
                        matched_rules.append(rule)
                except re.error:
                    # 跳过无效的正则表达式
                    continue
            elif rule["type"] == RuleType.KEYWORD.value:
                if rule["content"] in request_text:
                    matched_rules.append(rule)

        # 5. 如果至少匹配一条规则，则通过
        if matched_rules:
            return ValidationResult.ALLOW, matched_rules
        else:
            return ValidationResult.REJECT, []

    def test_pattern(self, pattern: str, test_text: str) -> Tuple[bool, bool, Optional[str]]:
        """
        测试模式是否匹配文本

        Args:
            pattern: 模式字符串（关键词或正则表达式）
            test_text: 测试文本

        Returns:
            (是否有效, 是否匹配, 错误信息)
        """
        is_regex = self.is_regex_pattern(pattern)

        if is_regex:
            # 验证正则表达式
            regex_pattern = pattern[1:-1]
            is_valid, error = self.validate_regex(regex_pattern)
            if not is_valid:
                return False, False, error

            # 测试匹配
            try:
                is_matched = bool(re.search(regex_pattern, test_text))
                return True, is_matched, None
            except re.error as e:
                return True, False, str(e)
        else:
            # 关键词匹配
            is_matched = pattern in test_text
            return True, is_matched, None
