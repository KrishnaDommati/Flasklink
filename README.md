# Flasklink Web Application

## Description

Flasklink is a modern web application that provides secure user registration and login, ensuring 
            your information is always safe. With a personalized dashboard, users can manage their 
            accounts, view updates, and access exclusive features. Flasklink now also includes a Notes 
            feature, allowing users to efficiently manage personal notes from their dashboard. It is built to offer a seamless 
            experience for managing your data with simplicity and security.
            
## Features

- **User Registration:** 
  - Register with a name, email, and password.
  - Passwords must be at least 6 characters long and include at least one uppercase letter, one digit, and one special symbol for enhanced security.
  - Passwords are hashed using bcrypt for security.
  - Email uniqueness check during registration.

- **User Login:** 
  - Log in using email or username and password.
  - Displays an error message for invalid credentials.

- **Dashboard:**
  - View and manage personal notes.
  - Time-based greeting based on the current hour (Good Morning, Good Afternoon, Good Evening).

- **Note Management:**
  - Add and delete notes.
  - Flash messages indicate the success or failure of note operations.

- **Logout:**
  - End the user session.

- **Account Deletion:**
  - Delete your account and remove all associated data.
