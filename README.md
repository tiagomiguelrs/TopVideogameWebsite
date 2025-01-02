# Top Videogames Library Application


## Description
This project is a web application built using the Flask framework. It allows users to add, edit, and delete entries for their top video games. The application fetches game details from the IGDB API and stores them in a SQLite database. Users can rank and review their favorite games, and the data is displayed on the homepage.

## Features
Add Videogames: Users can search for video games by title, fetch details from the IGDB API, and add them to the library.

Edit Videogames: Users can update the ranking and review of existing video games in the library.

Delete Videogames: Users can delete video games from the library.

Data Storage: Stores video game data in a SQLite database.

Bootstrap Integration: Uses Flask-Bootstrap to style the application.

Form Validation: Validates form inputs using Flask-WTF and WTForms.

## How It Works
Home Page: The home page displays a list of all video games in the library, ordered by their ranking.

Add Videogame: The `/add` route displays a form where users can enter the title of a video game. The application fetches game details from the IGDB API and displays a list of matching games for the user to select.

Select Videogame: The `/select/<int:_id>` route fetches detailed information about the selected game from the IGDB API and adds it to the database.

Edit Videogame: The `/edit/<int:_id>` route displays a form where users can update the ranking and review of an existing video game.

Delete Videogame: The `/delete/<int:_id>` route deletes a video game from the database based on its ID.

Database Management: Uses SQLAlchemy to manage the SQLite database, including creating tables and handling CRUD operations.
