from scraper import dbs
from scraper import app


if __name__ =='__main__':
    dbs.create_all()
    app.run(debug=True, port=1200)