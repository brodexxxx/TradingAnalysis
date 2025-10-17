"""
Test script to verify the updated trading analysis with current market prices
"""
import sys
from data_fetcher import symbols
from trading_analysis import analyze_symbol

def test_analysis():
    print("=" * 80)
    print("TESTING UPDATED TRADING ANALYSIS SYSTEM")
    print("=" * 80)
    
    # Test Sensex analysis
    symbol_name = 'Sensex'
    symbol = symbols[symbol_name]
    
    print(f"\n🔍 Analyzing {symbol_name}...")
    result = analyze_symbol(symbol_name, symbol)
    
    if result:
        print("\n✅ Analysis Successful!")
        print("-" * 80)
        
        # Test 1: Current Price
        print(f"\n1️⃣ CURRENT PRICE TEST:")
        print(f"   Current Price: ₹{result['price']:.2f}")
        if result['price'] >= 84000 and result['price'] <= 85000:
            print("   ✅ PASS - Price is in expected range (₹84,000 - ₹85,000)")
        else:
            print(f"   ⚠️  WARNING - Price {result['price']:.2f} outside expected range")
        
        # Test 2: Hold Range
        print(f"\n2️⃣ HOLD RANGE TEST:")
        print(f"   Hold Range: {result['hold_range']}")
        if '₹' in result['hold_range']:
            print("   ✅ PASS - Hold range includes currency symbol")
        else:
            print("   ❌ FAIL - Hold range missing currency symbol")
        
        # Test 3: Hold Time
        print(f"\n3️⃣ HOLD TIME TEST:")
        print(f"   Hold Time: {result['hold_time']}")
        if '₹' in result['hold_time'] or 'Target' in result['hold_time'] or 'Range' in result['hold_time']:
            print("   ✅ PASS - Hold time includes contextual information")
        else:
            print("   ⚠️  WARNING - Hold time may not have contextual info")
        
        # Test 4: Option Targets
        print(f"\n4️⃣ OPTION TARGETS TEST:")
        if 'option_targets' in result:
            targets = result['option_targets']
            
            if 'recommendation' in targets:
                rec = targets['recommendation']
                print(f"   Type: {rec['type']}")
                print(f"   Strike: {rec['strike']}")
                print(f"   Current Price: ₹{rec['current_price']}")
                print(f"   Entry Premium: ₹{rec['entry_premium']}")
                
                print(f"\n   📈 Profit Points:")
                for i, point in enumerate(rec['profit_points'], 1):
                    print(f"   Target {i}: Sensex @ ₹{point['underlying_price']}")
                    print(f"      Premium: ₹{point['expected_premium']} | Profit: ₹{point['profit']} ({point['profit_percent']}%)")
                
                # Verify profit points are reasonable
                if len(rec['profit_points']) == 3:
                    print("\n   ✅ PASS - All 3 profit points present")
                    
                    # Check if profit points are in ascending order for CALL
                    if rec['type'] == 'CALL':
                        prices = [p['underlying_price'] for p in rec['profit_points']]
                        if prices[0] < prices[1] < prices[2]:
                            print("   ✅ PASS - Profit points in correct ascending order")
                        else:
                            print("   ❌ FAIL - Profit points not in correct order")
                else:
                    print(f"   ❌ FAIL - Expected 3 profit points, got {len(rec['profit_points'])}")
                    
            elif 'entry_signals' in targets:
                entry = targets['entry_signals']
                print(f"   Mode: HOLD/MONITORING")
                print(f"   Call Entry: ₹{entry['call_entry']} CE")
                print(f"   Put Entry: ₹{entry['put_entry']} PE")
                print(f"   Range: {entry['monitoring_range']}")
                if 'call_trigger' in entry:
                    print(f"   Call Trigger: {entry['call_trigger']}")
                    print(f"   Put Trigger: {entry['put_trigger']}")
                print("   ✅ PASS - Entry signals present")
        else:
            print("   ❌ FAIL - No option targets found")
        
        # Test 5: Overall Summary
        print(f"\n5️⃣ OVERALL SUMMARY:")
        print(f"   Symbol: {result['symbol']}")
        print(f"   Action: {result['action']}")
        print(f"   Confidence: {result['confidence']:.1%}")
        print(f"   Phase: {result['phase']}")
        print(f"   RSI: {result['rsi']:.1f}")
        print(f"   Trend Strength: {result['trend_strength']}/4")
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED!")
        print("=" * 80)
        
        return True
    else:
        print("\n❌ Analysis Failed - No result returned")
        return False

if __name__ == "__main__":
    try:
        success = test_analysis()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
