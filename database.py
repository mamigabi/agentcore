import os
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseHistory:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables.")
        self.supabase: Client = create_client(url, key)
        self.table = "conversations"

    def add_message(self, session_id: str, role: str, content: str):
        try:
            data = {
                "session_id": session_id,
                "role": role,
                "content": content
                # created_at is automatic in Supabase
            }
            self.supabase.table(self.table).insert(data).execute()
        except Exception as e:
            print(f"Error adding message to Supabase: {e}")

    def get_history(self, session_id: str):
        try:
            response = self.supabase.table(self.table) \
                .select("*") \
                .eq("session_id", session_id) \
                .order("created_at", desc=False) \
                .execute()
            return response.data
        except Exception as e:
            print(f"Error fetching history from Supabase: {e}")
            return []
