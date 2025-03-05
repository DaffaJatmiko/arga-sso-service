from authlib.integrations.starlette_client import OAuth
from src.core.config import settings

class OAuthProvider:
    """Provider for OAuth authentication services"""
    
    def __init__(self):
        self.oauth = OAuth()
        self._configure_providers()
    
    def _configure_providers(self):
        """Configure supported OAuth providers"""
        self.oauth.register(
            name='google',
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'}
        )
        
        # Future providers can be added here
        # self.oauth.register(
        #     name='github',
        #     ...
        # )
    
    @property
    def google(self):
        """Get Google OAuth client"""
        return self.oauth.google

# Create a singleton instance
oauth_provider = OAuthProvider()