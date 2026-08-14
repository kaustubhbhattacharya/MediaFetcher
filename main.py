"""
By Kaustubh Bhattacharya
   Uploaded on: 14/08/26

This is a research and learning project created by Kaustubh Bhattacharya
for educational purposes. The project was developed to learn Python,
GUI development, database integration, media downloading, and CI/CD. 
Please read README.MD and DISCLAIMER.md for appropriate use.

"""

from app import MediaFetcherApp
from database import init_db

if __name__ == "__main__":
    init_db()
    app_mainGUI = MediaFetcherApp()
    app_mainGUI.mainloop()  