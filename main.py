from app import MediaFetcherApp
from database import init_db

if __name__ == "__main__":
    init_db()
    app_mainGUI = MediaFetcherApp()
    app_mainGUI.mainloop()  