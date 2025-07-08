from supabase import create_client
from django.conf import settings

url = settings.SUPABASE_URL
key = settings.SUPABASE_KEY
keyadmin = settings.SUPABASE_SERVICE_ROLE_KEY

supabase = create_client(url, key)

supabase_admin = create_client(url, keyadmin)
