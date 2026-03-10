import os
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

class SupabaseHistory:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables.")
        self.supabase: Client = create_client(url, key)
        self.table = "conversations"
        self.embeddings_model = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004", 
            google_api_key=os.environ.get("GEMINI_API_KEY")
        )

    def add_message(self, session_id: str, role: str, content: str):
        try:
            data = {
                "session_id": session_id,
                "role": role,
                "content": content
            }
            self.supabase.table(self.table).insert(data).execute()
            
            try:
                vector = self.embeddings_model.embed_query(content)
                embed_data = {
                    "session_id": session_id,
                    "content": content,
                    "embedding": vector
                }
                self.supabase.table("embeddings").insert(embed_data).execute()
            except Exception as embed_e:
                print(f"Error adding semantic memory: {embed_e}")
                
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

    def search_semantic_memory(self, query: str, limit: int = 5):
        try:
            query_embedding = self.embeddings_model.embed_query(query)
            response = self.supabase.rpc(
                "match_embeddings", 
                {
                    "query_embedding": query_embedding, 
                    "match_threshold": 0.5, 
                    "match_count": limit
                }
            ).execute()
            return response.data
        except Exception as e:
            print(f"Error searching semantic memory: {e}")
            return []
