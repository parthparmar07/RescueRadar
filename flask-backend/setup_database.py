import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    """Set up the Supabase database schema"""
    try:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_API_KEY')
        
        print(f"Connecting to Supabase: {url}")
        supabase: Client = create_client(url, key)
        
        # Read the SQL schema file
        with open('database_schema.sql', 'r') as f:
            schema_sql = f.read()
        
        print("Executing database schema...")
        
        # Execute the schema (Note: This requires service role key for DDL operations)
        # For production, you should run this SQL directly in Supabase SQL Editor
        try:
            # Try to create tables using RPC if available
            result = supabase.rpc('exec_sql', {'sql': schema_sql}).execute()
            print("✅ Database schema executed successfully!")
        except Exception as rpc_error:
            print(f"RPC method not available: {rpc_error}")
            print("⚠️  Please run the SQL schema manually in Supabase SQL Editor:")
            print("1. Go to https://supabase.com/dashboard")
            print("2. Open your project")
            print("3. Go to SQL Editor")
            print("4. Copy and paste the contents of database_schema.sql")
            print("5. Click 'Run'")
        
        # Test if tables exist by trying to query them
        print("\nTesting database connectivity...")
        
        try:
            # Test reports table
            result = supabase.table('reports').select('id').limit(1).execute()
            print("✅ Reports table is accessible")
        except Exception as e:
            print(f"❌ Reports table error: {e}")
        
        try:
            # Test notifications table
            result = supabase.table('notifications').select('id').limit(1).execute()
            print("✅ Notifications table is accessible")
        except Exception as e:
            print(f"❌ Notifications table error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Setting up RescueRadar Database...\n")
    setup_database()
    print("\n🏁 Database setup completed!")
