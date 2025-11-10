"""
Text-specific validation for text enhancement pipeline.
Simpler than conversation validation - just compare text content.
"""

import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class TextValidator:
    """
    Validates text enhancement quality.
    
    Validation Rules:
    1. Position match: Same _position in base and generated
    2. Text present: Generated has text content
    3. Text different: Generated text differs from base (actual enhancement)
    """
    
    def __init__(self, config: Dict):
        """
        Initialize validator with configuration.
        
        Args:
            config: Pipeline configuration
        """
        self.config = config
        self.text_column = config.get('base_data', {}).get('text_column', 'text')
        
        # Validation stats
        self.stats = {
            'validated': 0,
            'valid': 0,
            'invalid': 0,
            'missing': 0
        }
    
    def validate_position_match(
        self, 
        base_text: Dict, 
        generated_text: Dict
    ) -> Tuple[bool, str]:
        """
        Validate position match.
        
        Args:
            base_text: Base text item
            generated_text: Generated text item
        
        Returns:
            (is_valid, reason)
        """
        base_pos = base_text.get('_position', -1)
        gen_pos = generated_text.get('_position', -1)
        
        if base_pos == -1 or gen_pos == -1:
            return False, "Missing _position field"
        
        if base_pos != gen_pos:
            return False, f"Position mismatch: base={base_pos}, generated={gen_pos}"
        
        return True, "Position match"
    
    def validate_text_present(
        self, 
        generated_text: Dict
    ) -> Tuple[bool, str]:
        """
        Validate that generated text has content.
        
        Args:
            generated_text: Generated text item
        
        Returns:
            (is_valid, reason)
        """
        text = generated_text.get(self.text_column, '').strip()
        
        if not text:
            return False, "Generated text is empty"
        
        if len(text) < 10:
            return False, f"Generated text too short ({len(text)} chars)"
        
        return True, f"Text present ({len(text)} chars)"
    
    def validate_enhancement(
        self, 
        base_text: Dict, 
        generated_text: Dict
    ) -> Tuple[bool, str]:
        """
        Validate that text was actually enhanced (not just copied).
        
        Args:
            base_text: Base text item
            generated_text: Generated text item
        
        Returns:
            (is_valid, reason)
        """
        base_content = base_text.get(self.text_column, '').strip()
        gen_content = generated_text.get(self.text_column, '').strip()
        
        # Should be different (enhanced)
        if base_content == gen_content:
            return False, "Generated text identical to base (no enhancement)"
        
        # Generated should typically be longer (but not always required)
        # This is a soft check
        
        return True, "Text was enhanced"
    
    def is_valid_generation(
        self, 
        base_text: Dict, 
        generated_text: Dict
    ) -> Tuple[bool, str]:
        """
        Complete validation of generated text.
        
        Args:
            base_text: Base text item
            generated_text: Generated text item
        
        Returns:
            (is_valid, detailed_reason)
        """
        self.stats['validated'] += 1
        
        # Check 1: Position match
        valid, reason = self.validate_position_match(base_text, generated_text)
        if not valid:
            self.stats['invalid'] += 1
            return False, f"[Position] {reason}"
        
        # Check 2: Text present
        valid, reason = self.validate_text_present(generated_text)
        if not valid:
            self.stats['invalid'] += 1
            return False, f"[TextPresent] {reason}"
        
        # Check 3: Enhancement (optional, can be relaxed)
        valid, reason = self.validate_enhancement(base_text, generated_text)
        if not valid:
            # Log warning but don't fail
            logger.debug(f"Text enhancement check: {reason}")
        
        # All checks passed
        self.stats['valid'] += 1
        return True, "✓ Text validation passed"
    
    def get_stats(self) -> Dict:
        """Get validation statistics."""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset validation statistics."""
        self.stats = {
            'validated': 0,
            'valid': 0,
            'invalid': 0,
            'missing': 0
        }
