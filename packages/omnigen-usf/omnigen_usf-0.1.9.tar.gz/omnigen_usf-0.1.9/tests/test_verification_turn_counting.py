"""
Test turn counting logic for conversation verification.
Ensures 100% accuracy in all scenarios including deep conversations.
"""

import sys
sys.path.insert(0, '/Users/ankitagaud/Desktop/US_INC/datagen/OmniGen/src')

from omnigen.verification.conversation_validator import ConversationValidator


def test_turn_counting():
    """Test turn counting with various conversation patterns."""
    
    config = {
        'generation': {
            'turn_range': {'min': 1, 'max': 100},
            'extension_mode': 'smart'
        }
    }
    
    validator = ConversationValidator(config)
    
    print("🧪 Testing Turn Counting Logic")
    print("=" * 60)
    
    # Test 1: Single turn
    print("\n✅ Test 1: Single turn")
    conv1 = {
        'conversations': [
            {'from': 'system', 'value': 'You are helpful'},
            {'from': 'user', 'value': 'Hello'},
            {'from': 'assistant', 'value': 'Hi!'}
        ]
    }
    turns1 = validator.count_turns(conv1)
    print(f"   Conversation: [system, user, assistant]")
    print(f"   Expected: 1 turn")
    print(f"   Got: {turns1} turn(s)")
    assert turns1 == 1, f"Expected 1, got {turns1}"
    print("   ✓ PASS")
    
    # Test 2: Multiple turns
    print("\n✅ Test 2: Three complete turns")
    conv2 = {
        'conversations': [
            {'from': 'system', 'value': 'System prompt'},
            {'from': 'user', 'value': 'Q1'},
            {'from': 'assistant', 'value': 'A1'},
            {'from': 'user', 'value': 'Q2'},
            {'from': 'assistant', 'value': 'A2'},
            {'from': 'user', 'value': 'Q3'},
            {'from': 'assistant', 'value': 'A3'}
        ]
    }
    turns2 = validator.count_turns(conv2)
    print(f"   Conversation: [system, user, assistant, user, assistant, user, assistant]")
    print(f"   Expected: 3 turns")
    print(f"   Got: {turns2} turn(s)")
    assert turns2 == 3, f"Expected 3, got {turns2}"
    print("   ✓ PASS")
    
    # Test 3: Incomplete turn
    print("\n✅ Test 3: Incomplete turn (not counted)")
    conv3 = {
        'conversations': [
            {'from': 'user', 'value': 'Q1'},
            {'from': 'assistant', 'value': 'A1'},
            {'from': 'user', 'value': 'Q2'}  # No assistant response
        ]
    }
    turns3 = validator.count_turns(conv3)
    print(f"   Conversation: [user, assistant, user]")
    print(f"   Expected: 1 turn (second incomplete)")
    print(f"   Got: {turns3} turn(s)")
    assert turns3 == 1, f"Expected 1, got {turns3}"
    print("   ✓ PASS")
    
    # Test 4: No turns (system only)
    print("\n✅ Test 4: No turns (system only)")
    conv4 = {
        'conversations': [
            {'from': 'system', 'value': 'System prompt only'}
        ]
    }
    turns4 = validator.count_turns(conv4)
    print(f"   Conversation: [system]")
    print(f"   Expected: 0 turns")
    print(f"   Got: {turns4} turn(s)")
    assert turns4 == 0, f"Expected 0, got {turns4}"
    print("   ✓ PASS")
    
    # Test 5: Deep conversation (100 turns)
    print("\n✅ Test 5: Deep conversation (100 turns)")
    deep_msgs = [{'from': 'system', 'value': 'System'}]
    for i in range(100):
        deep_msgs.append({'from': 'user', 'value': f'Q{i+1}'})
        deep_msgs.append({'from': 'assistant', 'value': f'A{i+1}'})
    
    conv5 = {'conversations': deep_msgs}
    turns5 = validator.count_turns(conv5)
    print(f"   Conversation: 100 user+assistant pairs")
    print(f"   Expected: 100 turns")
    print(f"   Got: {turns5} turn(s)")
    assert turns5 == 100, f"Expected 100, got {turns5}"
    print("   ✓ PASS")
    
    # Test 6: Empty conversation
    print("\n✅ Test 6: Empty conversation")
    conv6 = {'conversations': []}
    turns6 = validator.count_turns(conv6)
    print(f"   Conversation: []")
    print(f"   Expected: 0 turns")
    print(f"   Got: {turns6} turn(s)")
    assert turns6 == 0, f"Expected 0, got {turns6}"
    print("   ✓ PASS")
    
    # Test 7: Alternating roles (human/gpt aliases)
    print("\n✅ Test 7: Role aliases (human/gpt)")
    conv7 = {
        'conversations': [
            {'from': 'human', 'value': 'Hi'},
            {'from': 'gpt', 'value': 'Hello'},
            {'from': 'human', 'value': 'How are you?'},
            {'from': 'gpt', 'value': 'Great!'}
        ]
    }
    turns7 = validator.count_turns(conv7)
    print(f"   Conversation: [human, gpt, human, gpt]")
    print(f"   Expected: 2 turns")
    print(f"   Got: {turns7} turn(s)")
    assert turns7 == 2, f"Expected 2, got {turns7}"
    print("   ✓ PASS")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)


def test_validation_rules():
    """Test validation rules with different configurations."""
    
    print("\n🧪 Testing Validation Rules")
    print("=" * 60)
    
    # Test 1: Smart mode (same turns allowed)
    print("\n✅ Test 1: Smart mode - same turns allowed")
    config_smart = {
        'generation': {
            'turn_range': {'min': 1, 'max': 10},
            'extension_mode': 'smart'
        }
    }
    validator_smart = ConversationValidator(config_smart)
    
    base = {'_position': 1, 'conversations': [
        {'from': 'user', 'value': 'Hi'},
        {'from': 'assistant', 'value': 'Hello'}
    ]}
    generated = {'_position': 1, 'conversations': [
        {'from': 'user', 'value': 'Hi'},
        {'from': 'assistant', 'value': 'Hello'}
    ]}
    
    valid, reason = validator_smart.is_valid_generation(base, generated)
    print(f"   Base: 1 turn, Generated: 1 turn")
    print(f"   Mode: smart")
    print(f"   Valid: {valid}")
    assert valid, f"Should be valid but got: {reason}"
    print("   ✓ PASS")
    
    # Test 2: Addition mode (must have more turns)
    print("\n✅ Test 2: Addition mode - must have MORE turns")
    config_add = {
        'generation': {
            'turn_range': {'min': 1, 'max': 10},
            'extension_mode': 'addition'
        }
    }
    validator_add = ConversationValidator(config_add)
    
    valid, reason = validator_add.is_valid_generation(base, generated)
    print(f"   Base: 1 turn, Generated: 1 turn")
    print(f"   Mode: addition")
    print(f"   Valid: {valid}")
    assert not valid, f"Should be invalid (same turns in addition mode)"
    print(f"   Reason: {reason}")
    print("   ✓ PASS (correctly invalid)")
    
    # Test 3: Turn range violation
    print("\n✅ Test 3: Turn range violation")
    config_range = {
        'generation': {
            'turn_range': {'min': 3, 'max': 5},
            'extension_mode': 'smart'
        }
    }
    validator_range = ConversationValidator(config_range)
    
    gen_many = {'_position': 1, 'conversations': [
        {'from': 'user', 'value': 'Q1'}, {'from': 'assistant', 'value': 'A1'},
        {'from': 'user', 'value': 'Q2'}, {'from': 'assistant', 'value': 'A2'},
        {'from': 'user', 'value': 'Q3'}, {'from': 'assistant', 'value': 'A3'},
        {'from': 'user', 'value': 'Q4'}, {'from': 'assistant', 'value': 'A4'},
        {'from': 'user', 'value': 'Q5'}, {'from': 'assistant', 'value': 'A5'},
        {'from': 'user', 'value': 'Q6'}, {'from': 'assistant', 'value': 'A6'},
    ]}  # 6 turns
    
    valid, reason = validator_range.is_valid_generation(base, gen_many)
    print(f"   Base: 1 turn, Generated: 6 turns")
    print(f"   Range: [3, 5]")
    print(f"   Valid: {valid}")
    assert not valid, f"Should be invalid (6 > max 5)"
    print(f"   Reason: {reason}")
    print("   ✓ PASS (correctly invalid)")
    
    print("\n" + "=" * 60)
    print("✅ ALL VALIDATION TESTS PASSED!")
    print("=" * 60)


if __name__ == '__main__':
    try:
        test_turn_counting()
        test_validation_rules()
        
        print("\n" + "🎉" * 20)
        print("\n✅ ALL TESTS PASSED - TURN COUNTING 100% ACCURATE!")
        print("\n" + "🎉" * 20)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
