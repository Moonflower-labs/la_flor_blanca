import os

class Config(object):   

       SECRET_KEY=os.getenv('SECRET_KEY')
       SESSION_COOKIE_SECURE = True  # Ensure the session cookie is only sent over HTTPS
       SESSION_COOKIE_HTTPONLY = True  # Protect the cookie from JavaScript access
       SESSION_COOKIE_SAMESITE = 'Lax'  # Set the SameSite attribute to Lax for better cross-site request protection
       SESSION_COOKIE_NAME= 'la-flor-blanca'  
    
class TestConfig(Config):
       TESTING=True

class ProductionConfig(Config):
        
       DATABASE_URL = os.getenv('DATABASE_URL')






