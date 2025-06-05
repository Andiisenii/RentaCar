from app import create_app, db
import os
from app import request, redirect
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Render përdor portin 10000 si default
    app.run(host='0.0.0.0', port=port)
    
    @app.before_request
    def redirect_www():
        if request.host.startswith("www."):
            new_url = request.url.replace("://www.", "://", 1)
        return redirect(new_url, code=301)