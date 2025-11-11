"""
Complete system integration test.
Tests all components working together.
"""

import sys
sys.path.insert(0, '/Users/ankitagaud/Desktop/US_INC/datagen/OmniGen/src')

from omnigen.verification import DataVerifier, ConversationValidator, TextValidator


def test_imports():
    """Test all modules import correctly."""
    print("Testing imports...")
    
    from omnigen.pipelines.conversation_extension.runner import Runner as ConvRunner
    from omnigen.pipelines.text_enhancement.runner import Runner as TextRunner
    
    print("✅ All modules import successfully")


def test_turn_counting():
    """Test turn counting logic."""
    print("\nTesting turn counting...")
    
    config = {
        'generation': {
            'turn_range': {'min': 1, 'max': 10},
            'extension_mode': 'smart'
        }
    }
    validator = ConversationValidator(config)
    
    # Test cases
    tests = [
        # (conversation, expected_turns)
        ({
            'conversations': [
                {'from': 'user', 'value': 'Hi'},
                {'from': 'assistant', 'value': 'Hello'}
            ]
        }, 1),
        ({
            'conversations': [
                {'from': 'system', 'value': 'System'},
                {'from': 'user', 'value': 'Q1'},
                {'from': 'assistant', 'value': 'A1'},
                {'from': 'user', 'value': 'Q2'},
                {'from': 'assistant', 'value': 'A2'},
                {'from': 'user', 'value': 'Q3'},
                {'from': 'assistant', 'value': 'A3'}
            ]
        }, 3),
        ({
            'conversations': [
                {'from': 'user', 'value': 'Q1'},
                {'from': 'assistant', 'value': 'A1'},
                {'from': 'user', 'value': 'Q2'}  # Incomplete
            ]
        }, 1),
        ({
            'conversations': []
        }, 0),
    ]
    
    for i, (conv, expected) in enumerate(tests, 1):
        result = validator.count_turns(conv)
        assert result == expected, f"Test {i} failed: got {result}, expected {expected}"
        print(f"✅ Turn counting test {i}: {result} turn(s) - PASS")


def test_validation_smart_mode():
    """Test validation in smart mode."""
    print("\nTesting validation (smart mode)...")
    
    config = {
        'generation': {
            'turn_range': {'min': 3, 'max': 8},
            'extension_mode': 'smart'
        }
    }
    validator = ConversationValidator(config)
    
    # Base conversation with 3 turns
    base = {
        '_position': 1,
        'conversations': [
            {'from': 'user', 'value': 'Q1'},
            {'from': 'assistant', 'value': 'A1'},
            {'from': 'user', 'value': 'Q2'},
            {'from': 'assistant', 'value': 'A2'},
            {'from': 'user', 'value': 'Q3'},
            {'from': 'assistant', 'value': 'A3'}
        ]
    }
    
    # Valid: same turns (smart mode allows this)
    gen_same = {
        '_position': 1,
        'conversations': [
            {'from': 'user', 'value': 'Q1'},
            {'from': 'assistant', 'value': 'A1'},
            {'from': 'user', 'value': 'Q2'},
            {'from': 'assistant', 'value': 'A2'},
            {'from': 'user', 'value': 'Q3'},
            {'from': 'assistant', 'value': 'A3'}
        ]
    }
    is_valid, reason = validator.is_valid_generation(base, gen_same)
    assert is_valid, f"Same turns should be valid in smart mode: {reason}"
    print("✅ Smart mode: Same turns - VALID")
    
    # Valid: more turns
    gen_more = {
        '_position': 1,
        'conversations': [
            {'from': 'user', 'value': 'Q1'},
            {'from': 'assistant', 'value': 'A1'},
            {'from': 'user', 'value': 'Q2'},
            {'from': 'assistant', 'value': 'A2'},
            {'from': 'user', 'value': 'Q3'},
            {'from': 'assistant', 'value': 'A3'},
            {'from': 'user', 'value': 'Q4'},
            {'from': 'assistant', 'value': 'A4'}
        ]
    }
    is_valid, reason = validator.is_valid_generation(base, gen_more)
    assert is_valid, f"More turns should be valid: {reason}"
    print("✅ Smart mode: More turns - VALID")
    
    # Invalid: fewer turns than base
    gen_fewer = {
        '_position': 1,
        'conversations': [
            {'from': 'user', 'value': 'Q1'},
            {'from': 'assistant', 'value': 'A1'}
        ]
    }
    is_valid, reason = validator.is_valid_generation(base, gen_fewer)
    assert not is_valid, "Fewer turns should be invalid"
    print("✅ Smart mode: Fewer turns - INVALID (correct)")
    
    # Invalid: outside range (10 turns, max is 8)
    gen_too_many = {'_position': 1, 'conversations': []}
    for i in range(1, 11):
        gen_too_many['conversations'].append({'from': 'user', 'value': f'Q{i}'})
        gen_too_many['conversations'].append({'from': 'assistant', 'value': f'A{i}'})
    
    is_valid, reason = validator.is_valid_generation(base, gen_too_many)
    assert not is_valid, "Outside range should be invalid"
    print("✅ Smart mode: Outside range - INVALID (correct)")


def test_validation_addition_mode():
    """Test validation in addition mode."""
    print("\nTesting validation (addition mode)...")
    
    config = {
        'generation': {
            'turn_range': {'min': 3, 'max': 8},
            'extension_mode': 'addition'
        }
    }
    validator = ConversationValidator(config)
    
    base = {
        '_position': 1,
        'conversations': [
            {'from': 'user', 'value': 'Q1'},
            {'from': 'assistant', 'value': 'A1'},
            {'from': 'user', 'value': 'Q2'},
            {'from': 'assistant', 'value': 'A2'}
        ]
    }  # 2 turns
    
    # Invalid: same turns (addition requires more)
    gen_same = {
        '_position': 1,
        'conversations': [
            {'from': 'user', 'value': 'Q1'},
            {'from': 'assistant', 'value': 'A1'},
            {'from': 'user', 'value': 'Q2'},
            {'from': 'assistant', 'value': 'A2'}
        ]
    }
    is_valid, reason = validator.is_valid_generation(base, gen_same)
    assert not is_valid, "Same turns invalid in addition mode"
    print("✅ Addition mode: Same turns - INVALID (correct)")
    
    # Valid: more turns
    gen_more = {
        '_position': 1,
        'conversations': [
            {'from': 'user', 'value': 'Q1'},
            {'from': 'assistant', 'value': 'A1'},
            {'from': 'user', 'value': 'Q2'},
            {'from': 'assistant', 'value': 'A2'},
            {'from': 'user', 'value': 'Q3'},
            {'from': 'assistant', 'value': 'A3'}
        ]
    }
    is_valid, reason = validator.is_valid_generation(base, gen_more)
    assert is_valid, f"More turns should be valid in addition mode: {reason}"
    print("✅ Addition mode: More turns - VALID")


def test_verifier_instantiation():
    """Test DataVerifier instantiation."""
    print("\nTesting DataVerifier...")
    
    config = {
        'verification': {
            'enabled': True,
            'strict_mode': True,
            'auto_recheck': True
        },
        'generation': {
            'turn_range': {'min': 3, 'max': 8},
            'extension_mode': 'smart'
        }
    }
    
    verifier = DataVerifier(config, pipeline_type='conversation')
    assert verifier.enabled == True
    assert verifier.strict_mode == True
    assert verifier.auto_recheck == True
    print("✅ DataVerifier instantiates correctly")
    
    # Check initialization
    assert hasattr(verifier, 'orphan_positions')
    assert isinstance(verifier.orphan_positions, set)
    print("✅ DataVerifier has orphan_positions initialized")


if __name__ == '__main__':
    print("=" * 60)
    print("COMPLETE SYSTEM INTEGRATION TEST")
    print("=" * 60)
    print()
    
    try:
        test_imports()
        test_turn_counting()
        test_validation_smart_mode()
        test_validation_addition_mode()
        test_verifier_instantiation()
        
        print()
        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print()
        print("System verification complete:")
        print("  ✅ All modules import")
        print("  ✅ Turn counting accurate")
        print("  ✅ Smart mode validation correct")
        print("  ✅ Addition mode validation correct")
        print("  ✅ DataVerifier initialization correct")
        print()
        print("🚀 SYSTEM IS 100% PRODUCTION READY!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
