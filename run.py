from app import create_app, db
import os

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Render përdor portin 10000 si default
    app.run(host='0.0.0.0', port=port)