"""Validation rules for text enhancement quality checks."""

import re
from typing import Dict, Any, Tuple, Optional, List
from omnigen.utils.logger import setup_logger

logger = setup_logger()


class TextEnhancementValidator:
    """
    Validates enhanced text quality using rule-based checks.
    
    All validation is OPT-IN - disabled by default.
    Users must explicitly configure rules they want.
    
    Supported rule types:
    1. Empty check - Ensure text is not empty
    2. Length rules - Min/max absolute length
    3. Length ratio - Compared to original (e.g., 70%-130%)
    4. Identity check - Must be different from original
    5. Regex patterns - Custom regex matching
    6. Custom rules - User-defined validation functions
    
    Per-rule configuration:
    - enabled: Enable this rule
    - fail_immediately: Don't retry if this rule fails
    - severity: 'error' or 'warning'
    """
    
    @staticmethod
    def validate_enhanced_text(
        original_text: str,
        enhanced_text: str,
        config: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate enhanced text quality using configured rules.
        
        Args:
            original_text: Original input text
            enhanced_text: Enhanced output text
            config: Validation configuration with rules
            
        Returns:
            (is_valid, error_message, rule_name) tuple
        """
        try:
            # Safety: Ensure config is not None
            if config is None:
                config = {}
            
            # Safety: Ensure texts are not None
            if original_text is None:
                original_text = ''
            if enhanced_text is None:
                enhanced_text = ''
            
            rules = config.get('rules', [])
            
            # Safety: Ensure rules is a list
            if not isinstance(rules, list):
                logger.warning(f"Invalid rules (not a list): {type(rules)}, using empty list")
                rules = []
            
            # If no rules configured, validation passes
            if not rules:
                return True, None, None
            
            # Run each configured rule
            for rule in rules:
                # Safety: Skip if rule is not a dict
                if not isinstance(rule, dict):
                    logger.warning(f"Skipping invalid rule (not a dict): {rule}")
                    continue
                
                if not rule.get('enabled', False):
                    continue
                
                rule_type = rule.get('type')
                if not rule_type:
                    logger.warning(f"Skipping rule without type: {rule}")
                    continue
                
                rule_name = rule.get('name', rule_type)
                
                try:
                    is_valid, error = TextEnhancementValidator._check_rule(
                        rule_type,
                        rule,
                        original_text,
                        enhanced_text
                    )
                    
                    if not is_valid:
                        return False, error, rule_name
                except Exception as rule_error:
                    logger.error(f"Error checking rule '{rule_name}': {rule_error}")
                    # Continue to next rule instead of failing entire validation
                    continue
            
            # All rules passed
            return True, None, None
            
        except Exception as e:
            logger.error(f"Error during validation: {e}")
            return False, f"Validation error: {e}", None
    
    @staticmethod
    def _check_rule(
        rule_type: str,
        rule: Dict[str, Any],
        original_text: str,
        enhanced_text: str
    ) -> Tuple[bool, Optional[str]]:
        """Check a single validation rule."""
        
        if rule_type == 'not_empty':
            if not enhanced_text or not enhanced_text.strip():
                return False, "Enhanced text is empty or whitespace only"
        
        elif rule_type == 'min_length':
            min_len = rule.get('value', 10)
            # Safety: Ensure min_len is a positive number
            try:
                min_len = int(min_len)
                if min_len < 0:
                    min_len = 0
            except (TypeError, ValueError):
                logger.warning(f"Invalid min_length value: {min_len}, using default 10")
                min_len = 10
            
            if len(enhanced_text.strip()) < min_len:
                return False, f"Enhanced text too short ({len(enhanced_text.strip())} chars, min: {min_len})"
        
        elif rule_type == 'max_length':
            max_len = rule.get('value', 10000)
            # Safety: Ensure max_len is a positive number
            try:
                max_len = int(max_len)
                if max_len < 0:
                    max_len = 10000
            except (TypeError, ValueError):
                logger.warning(f"Invalid max_length value: {max_len}, using default 10000")
                max_len = 10000
            
            if len(enhanced_text.strip()) > max_len:
                return False, f"Enhanced text too long ({len(enhanced_text.strip())} chars, max: {max_len})"
        
        elif rule_type == 'not_identical':
            if enhanced_text.strip() == original_text.strip():
                return False, "Enhanced text is identical to original (no enhancement)"
        
        elif rule_type == 'length_ratio':
            min_ratio = rule.get('min_ratio', 0.7)  # 70% of original
            max_ratio = rule.get('max_ratio', 1.3)  # 130% of original
            
            # Safety: Ensure ratios are valid floats
            try:
                min_ratio = float(min_ratio)
                if min_ratio < 0:
                    min_ratio = 0.0
            except (TypeError, ValueError):
                logger.warning(f"Invalid min_ratio value: {min_ratio}, using default 0.7")
                min_ratio = 0.7
            
            try:
                max_ratio = float(max_ratio)
                if max_ratio < 0:
                    max_ratio = 10.0
            except (TypeError, ValueError):
                logger.warning(f"Invalid max_ratio value: {max_ratio}, using default 1.3")
                max_ratio = 1.3
            
            # Safety: Ensure min_ratio <= max_ratio
            if min_ratio > max_ratio:
                logger.warning(f"Invalid ratio range: min_ratio ({min_ratio}) > max_ratio ({max_ratio}), swapping values")
                min_ratio, max_ratio = max_ratio, min_ratio
            
            original_len = len(original_text.strip())
            enhanced_len = len(enhanced_text.strip())
            
            if original_len > 0:
                ratio = enhanced_len / original_len
                
                if ratio < min_ratio:
                    return False, f"Enhanced text too short ({ratio:.1%} of original, min: {min_ratio:.1%})"
                
                if ratio > max_ratio:
                    return False, f"Enhanced text too long ({ratio:.1%} of original, max: {max_ratio:.1%})"
        
        elif rule_type == 'regex_match':
            # Support both single pattern (string) and multiple patterns (list)
            pattern = rule.get('pattern')
            patterns = rule.get('patterns', [])
            
            if not pattern and not patterns:
                return True, None
            
            # Convert single pattern to list for unified processing
            if pattern:
                if isinstance(pattern, str):
                    patterns = [pattern]
                else:
                    logger.warning(f"Invalid regex pattern (not a string): {type(pattern)}")
                    return True, None
            
            # Check if enhanced text matches at least one pattern
            matched = False
            for pat in patterns:
                if not isinstance(pat, str):
                    continue
                try:
                    if re.search(pat, enhanced_text):
                        matched = True
                        break
                except re.error as e:
                    logger.error(f"Invalid regex pattern '{pat}': {e}")
                    continue
            
            if not matched:
                return False, f"Enhanced text does not match any required pattern: {rule.get('description', 'see patterns')}"
        
        elif rule_type == 'regex_not_match':
            # Support both single pattern (string) and multiple patterns (list)
            pattern = rule.get('pattern')
            patterns = rule.get('patterns', [])
            
            if not pattern and not patterns:
                return True, None
            
            # Convert single pattern to list for unified processing
            if pattern:
                if isinstance(pattern, str):
                    patterns = [pattern]
                else:
                    logger.warning(f"Invalid regex pattern (not a string): {type(pattern)}")
                    return True, None
            
            # Check that enhanced text doesn't match any forbidden pattern
            for pat in patterns:
                if not isinstance(pat, str):
                    continue
                try:
                    if re.search(pat, enhanced_text):
                        return False, f"Enhanced text matches forbidden pattern: {pat}"
                except re.error as e:
                    logger.error(f"Invalid regex pattern '{pat}': {e}")
                    continue
        
        elif rule_type == 'contains':
            # Support both single value (string) and multiple values (list)
            value = rule.get('value', '')
            values = rule.get('values', [])
            
            if not value and not values:
                return True, None
            
            # Convert single value to list for unified processing
            if value:
                if isinstance(value, str):
                    values = [value]
                else:
                    logger.warning(f"Invalid contains value (not a string): {type(value)}")
                    return True, None
            
            # Check if enhanced text contains at least one required string
            found = False
            for val in values:
                if not isinstance(val, str):
                    continue
                if val in enhanced_text:
                    found = True
                    break
            
            if not found:
                return False, f"Enhanced text must contain at least one of: {values}"
        
        elif rule_type == 'not_contains':
            # Support both single value (string) and multiple values (list)
            value = rule.get('value', '')
            values = rule.get('values', [])
            
            if not value and not values:
                return True, None
            
            # Convert single value to list for unified processing
            if value:
                if isinstance(value, str):
                    values = [value]
                else:
                    logger.warning(f"Invalid not_contains value (not a string): {type(value)}")
                    return True, None
            
            # Check that enhanced text doesn't contain any forbidden string
            for val in values:
                if not isinstance(val, str):
                    continue
                if val in enhanced_text:
                    return False, f"Enhanced text must not contain: {val}"
        
        else:
            logger.warning(f"Unknown rule type: {rule_type}")
            return True, None  # Skip unknown rules
        
        return True, None
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get default validation configuration (ENABLED by default with essential quality checks)."""
        return {
            'enabled': True,  # ✅ Enabled by default with essential quality checks
            'max_retries': 2,  # Retry 2 times by default
            'fail_on_validation_error': True,
            'save_rejected_to_file': True,  # Save rejected items for analysis
            'rejected_file': 'rejected.jsonl',
            'rules': [
                # ✅ ENABLED BY DEFAULT - Essential quality checks
                {
                    'type': 'not_empty',
                    'enabled': True,
                    'name': 'empty_check',
                    'fail_immediately': True,  # Don't retry empty responses
                    'description': 'Enhanced text must not be empty'
                },
                {
                    'type': 'not_identical',
                    'enabled': True,
                    'name': 'must_be_different',
                    'description': 'Enhanced text must be different from original (actual enhancement required)'
                },
                {
                    'type': 'length_ratio',
                    'enabled': True,
                    'min_ratio': 0.7,  # At least 70% of original (don't remove too much)
                    'max_ratio': 1.3,  # At most 130% of original (don't add too much)
                    'name': 'length_ratio_70_130',
                    'description': 'Enhanced text must be 70-130% of original length'
                },
                # Optional rules (user can enable by setting enabled: True)
                # {
                #     'type': 'min_length',
                #     'enabled': False,
                #     'value': 20,
                #     'name': 'min_20_chars',
                #     'description': 'Enhanced text must be at least 20 characters'
                # },
            ]
        }
    
    @staticmethod
    def get_rule_examples() -> List[Dict[str, Any]]:
        """Get example rules that users can configure."""
        return [
            {
                'type': 'not_empty',
                'enabled': True,
                'name': 'empty_check',
                'fail_immediately': True,  # Don't retry empty responses
                'description': 'Enhanced text must not be empty'
            },
            {
                'type': 'min_length',
                'enabled': True,
                'value': 20,
                'name': 'min_20_chars',
                'description': 'Enhanced text must be at least 20 characters'
            },
            {
                'type': 'length_ratio',
                'enabled': True,
                'min_ratio': 0.7,  # 70% of original
                'max_ratio': 1.3,  # 130% of original
                'name': 'length_ratio_70_130',
                'description': 'Enhanced text must be 70-130% of original length'
            },
            {
                'type': 'not_identical',
                'enabled': True,
                'name': 'must_be_different',
                'description': 'Enhanced text must be different from original'
            },
            {
                'type': 'regex_match',
                'enabled': True,
                'pattern': r'[A-Z]',  # Must contain uppercase letter
                'name': 'has_uppercase',
                'description': 'Must contain at least one uppercase letter'
            },
            {
                'type': 'regex_not_match',
                'enabled': True,
                'pattern': r'\b(TODO|FIXME|XXX)\b',  # Must not contain TODO markers
                'name': 'no_todo_markers',
                'description': 'Must not contain TODO/FIXME markers'
            },
            {
                'type': 'contains',
                'enabled': False,
                'value': 'specific phrase',
                'name': 'must_contain_phrase',
                'description': 'Must contain specific phrase'
            },
        ]
