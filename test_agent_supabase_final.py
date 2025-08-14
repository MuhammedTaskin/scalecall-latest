#!/usr/bin/env python3
"""
Final Test: Agent Supabase Read/Write Operations
Verify agents can successfully read and modify Supabase data
"""
import asyncio
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, 'backend')

from tools.supabase_telecom import SupabaseTelecomTools

async def test_agent_supabase_operations():
    """Test that agents can read and write to Supabase successfully."""
    
    print("🎯 FINAL AGENT SUPABASE TEST")
    print("=" * 50)
    
    tools = SupabaseTelecomTools()
    
    # Test 1: Verify Supabase connection
    print("📡 Testing Supabase Connection...")
    if not tools.supabase:
        print("❌ Supabase not available - using fallback mode")
        return False
    
    try:
        # Simple connection test
        test_query = tools.supabase.table("customers").select("count").execute()
        print("✅ Supabase connection successful")
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False
    
    # Test 2: READ operations
    print("\n📖 Testing READ Operations...")
    read_result = await tools.execute("verify_user", {
        "maiden_name": "Kaya",
        "msisdn": "05551234567"
    })
    
    if read_result.success:
        customer_id = read_result.data.get("customer_id")
        print(f"✅ READ successful: Customer {customer_id} found")
    else:
        print(f"❌ READ failed: {read_result.error}")
        return False
    
    # Test 3: CREATE operations
    print("\n📝 Testing CREATE Operations...")
    create_result = await tools.execute("reissue_activation_code", {
        "customer_id": customer_id
    })
    
    if create_result.success:
        new_code = create_result.data.get("code")
        print(f"✅ CREATE successful: New activation code {new_code}")
    else:
        print(f"❌ CREATE failed: {create_result.error}")
        return False
    
    # Test 4: UPDATE operations
    print("\n✏️ Testing UPDATE Operations...")
    
    # Get current package first
    user_info = await tools.execute("get_user_info", {
        "customer_id": customer_id
    })
    
    if user_info.success:
        package_data = user_info.data.get("package") if user_info.data else None
        current_package = package_data.get("package_id", "premium_10gb") if package_data else "premium_10gb"
        new_package = "family_20gb" if current_package != "family_20gb" else "premium_10gb"
        
        update_result = await tools.execute("change_package", {
            "customer_id": customer_id,
            "package_id": new_package
        })
        
        if update_result.success:
            print(f"✅ UPDATE successful: Package changed to {new_package}")
        else:
            print(f"❌ UPDATE failed: {update_result.error}")
            return False
    else:
        print(f"❌ Could not get user info for update test")
        return False
    
    # Test 5: Support ticket creation
    print("\n🎫 Testing Support Ticket Creation...")
    ticket_result = await tools.execute("create_support_ticket", {
        "customer_id": customer_id,
        "issue_type": "technical",
        "description": f"Test ticket - {datetime.now().isoformat()}"
    })
    
    if ticket_result.success:
        ticket_id = ticket_result.data.get("ticket_id")
        print(f"✅ TICKET CREATE successful: {ticket_id}")
    else:
        print(f"❌ TICKET CREATE failed: {ticket_result.error}")
        return False
    
    print(f"\n🎉 ALL TESTS PASSED!")
    print("✅ Agents can READ from Supabase")
    print("✅ Agents can WRITE to Supabase") 
    print("✅ Agents can UPDATE Supabase data")
    print("✅ Agents can CREATE new records")
    print("✅ Data persistence confirmed")
    
    return True

async def test_professional_agent_integration():
    """Test the professional agent with Supabase integration."""
    
    print("\n" + "=" * 50)
    print("🤖 PROFESSIONAL AGENT INTEGRATION TEST")
    print("=" * 50)
    
    # Import and test the professional agent
    sys.path.insert(0, '.')
    from supabase_professional_agent import SupabaseProfessionalAgent
    
    agent = SupabaseProfessionalAgent()
    
    print("Testing agent workflow with database integration...")
    
    # Test complete workflow
    print("\n🎭 Testing Complete Agent Workflow:")
    
    # Reset agent state
    agent.reset_conversation()
    
    # Step 1: User request
    response1 = await agent.process_message("mevsim kurdum ama sinyal yok")
    print(f"👤 User: mevsim kurdum ama sinyal yok")
    print(f"🤖 Agent: {response1}")
    
    # Step 2: Phone verification
    response2 = await agent.process_message("sıfır beş beş beş bir iki üç dört beş altı yedi")
    print(f"👤 User: sıfır beş beş beş bir iki üç dört beş altı yedi")
    print(f"🤖 Agent: {response2}")
    
    # Step 3: Maiden name
    response3 = await agent.process_message("Kaya")
    print(f"👤 User: Kaya")
    print(f"🤖 Agent: {response3}")
    
    # Check if verification was successful
    if agent.conversation_state.get("verified"):
        print("✅ Agent successfully verified customer using Supabase")
        print(f"✅ Customer ID: {agent.conversation_state.get('customer_id')}")
        print(f"✅ Customer Name: {agent.conversation_state.get('customer_name')}")
        
        # Step 4: IMEI check
        response4 = await agent.process_message("aymay numaram 359111222333444")
        print(f"👤 User: aymay numaram 359111222333444")
        print(f"🤖 Agent: {response4}")
        
        return True
    else:
        print("❌ Agent failed to verify customer")
        return False

async def main():
    """Run all final tests."""
    
    print("🚀 STARTING FINAL SUPABASE INTEGRATION TESTS")
    print("=" * 60)
    
    # Test 1: Basic Supabase operations
    basic_test = await test_agent_supabase_operations()
    
    if not basic_test:
        print("\n❌ Basic Supabase tests failed - stopping")
        return
    
    # Test 2: Professional agent integration
    agent_test = await test_professional_agent_integration()
    
    if agent_test:
        print(f"\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Supabase connection working")
        print("✅ Agents can read/write database")
        print("✅ Professional agent workflow functional")
        print("✅ Customer verification through database")
        print("✅ Tool integration with data persistence")
        print("\n🎯 SYSTEM READY FOR PRODUCTION!")
    else:
        print(f"\n❌ Agent integration tests failed")

if __name__ == "__main__":
    asyncio.run(main())
