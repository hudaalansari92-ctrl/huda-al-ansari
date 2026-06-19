
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*70)
print(" Quick Test - Import Fix Verification")
print("="*70)
print()

# Test 1: Import check
print("Test 1: Checking imports...")
try:
    from decision_tree_viz import (
        create_decision_tree_diagram,
        create_simple_decision_tree_flow,
        create_decision_rules_table
    )
    print("[OK] All imports successful!")
    print(f"   • create_decision_tree_diagram: OK")
    print(f"   • create_simple_decision_tree_flow: OK")
    print(f"   • create_decision_rules_table: OK")
except ImportError as e:
    print(f"[FAIL] Import failed: {e}")
    sys.exit(1)

print()

# Test 2: Function execution
print("Test 2: Testing functions...")
try:
    # Create visualizations
    fig1 = create_decision_tree_diagram()
    print(f"[OK] create_decision_tree_diagram() works ({len(fig1.data)} traces)")
    
    fig2 = create_simple_decision_tree_flow()
    print(f"[OK] create_simple_decision_tree_flow() works ({len(fig2.data)} traces)")
    
    fig3 = create_decision_rules_table()
    print(f"[OK] create_decision_rules_table() works ({len(fig3.data)} trace)")
except Exception as e:
    print(f"[FAIL] Function test failed: {e}")
    sys.exit(1)

print()

# Test 3: With final_decision
print("Test 3: Testing with final_decision...")
try:
    final_decision = {
        'final_risk_level': 'CRITICAL',
        'confidence': 0.90
    }
    
    fig1 = create_decision_tree_diagram(final_decision)
    print(f"[OK] Tree diagram with active path works")
    
    fig2 = create_decision_rules_table(final_decision)
    print(f"[OK] Rules table with highlighted rule works")
except Exception as e:
    print(f"[FAIL] final_decision test failed: {e}")
    sys.exit(1)

print()

# Test 4: App.py syntax
print("Test 4: Checking app.py syntax...")
try:
    import py_compile
    py_compile.compile('app.py', doraise=True)
    print("[OK] app.py syntax is correct")
except Exception as e:
    print(f"[FAIL] app.py syntax error: {e}")
    sys.exit(1)

print()
print("="*70)
print(" [OK] ALL TESTS PASSED!")
print("="*70)
print()
print("The import error is FIXED!")
print()
print("You can now run:")
print("  streamlit run app.py")
print()
print("="*70)
