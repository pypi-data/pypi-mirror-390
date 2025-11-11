#!/usr/bin/env python3
"""
SpiralLogic CLI - Command line interface for testing SpiralLogic programs
"""

import sys
import json
import argparse
from pathlib import Path
from .spirallogic_runtime import SpiralLogic

def main():
    parser = argparse.ArgumentParser(description="SpiralLogic Runtime CLI")
    parser.add_argument("ritual_file", help="SpiralLogic ritual file to execute")
    parser.add_argument("--user", default="test_user", help="User ID")
    parser.add_argument("--session", help="Session ID (auto-generated if not provided)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Check if file exists
    ritual_path = Path(args.ritual_file)
    if not ritual_path.exists():
        print(f"Error: Ritual file '{args.ritual_file}' not found")
        sys.exit(1)
    
    # Read ritual program
    try:
        with open(ritual_path, 'r') as f:
            ritual_code = f.read()
    except Exception as e:
        print(f"Error reading ritual file: {e}")
        sys.exit(1)
    
    # Initialize SpiralLogic runtime
    print("🔮 Initializing SpiralLogic Runtime...")
    sl = SpiralLogic()
    
    if args.verbose:
        print(f"📄 Executing ritual: {ritual_path.name}")
        print(f"👤 User: {args.user}")
        print(f"📝 Ritual code preview:")
        print("-" * 40)
        print(ritual_code[:200] + "..." if len(ritual_code) > 200 else ritual_code)
        print("-" * 40)
    
    # Execute ritual
    try:
        result = sl.execute(ritual_code, user_id=args.user, session_id=args.session)
        
        print("\n✨ Ritual Execution Complete!")
        print("=" * 50)
        
        if result["success"]:
            print("✅ Status: SUCCESS")
            print(f"🆔 Ritual ID: {result['ritual_id']}")
            print(f"🗣️  Voice: {result['context']['voice']}")
            print(f"🎯 Intent: {result['context']['intent']}")
            print(f"🚨 Crisis Active: {result['context']['crisis_active']}")
            
            print(f"\n📋 Steps Executed ({len(result['results'])}):")
            for i, step_result in enumerate(result['results'], 1):
                step_type = step_result.get('type', 'unknown')
                success = step_result.get('success', False)
                status = "✅" if success else "❌"
                print(f"  {i}. {status} {step_type}")
                
                if step_type == "consent.request":
                    scopes = step_result.get('scopes', [])
                    print(f"     Scopes: {', '.join(scopes)}")
                    print(f"     Granted: {success}")
                
                elif step_type == "voice.speak":
                    message = step_result.get('message', '')
                    crisis = step_result.get('crisis_detected', False)
                    print(f"     Message: {message[:100]}{'...' if len(message) > 100 else ''}")
                    if crisis:
                        print("     ⚠️  CRISIS DETECTED IN MESSAGE")
                
                elif step_type == "memory.store":
                    if success:
                        memory_id = step_result.get('memory_id', 'unknown')
                        memory_type = step_result.get('memory_type', 'unknown')
                        print(f"     Stored: {memory_type} memory [{memory_id[:8]}...]")
                
                elif step_type == "crisis_response":
                    response_data = step_result.get('data', {})
                    mode = response_data.get('mode', 'unknown')
                    print(f"     🚨 Crisis Response Mode: {mode}")
                    print(f"     Message: {response_data.get('message', '')}")
                
                if args.verbose and 'error' in step_result:
                    print(f"     ❌ Error: {step_result['error']}")
        
        else:
            print("❌ Status: FAILED")
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        print("\n📊 Consent Status:")
        consent_granted = result.get('context', {}).get('consent_granted', {})
        if consent_granted:
            for scope, granted in consent_granted.items():
                status = "✅" if granted else "❌"
                print(f"  {status} {scope}")
        else:
            print("  No consent requests processed")
        
        if args.verbose:
            print("\n📄 Full Result JSON:")
            print(json.dumps(result, indent=2))
            
            # Show attestation log location
            print(f"\n🔗 Attestation Log: spirallogic_attestations.log")
            print(f"💾 Memory Database: spirallogic_memory.db")
        
    except Exception as e:
        print(f"❌ Runtime Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()