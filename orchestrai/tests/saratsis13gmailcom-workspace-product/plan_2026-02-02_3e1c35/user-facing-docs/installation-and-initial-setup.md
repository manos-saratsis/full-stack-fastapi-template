# Installation and Initial Setup

Get the Full Stack FastAPI Template running on your local machine in minutes. This guide will walk you through everything from downloading the project to accessing your new application.

## Prerequisites

Before you begin, ensure you have the following installed on your computer:

- **Docker Desktop** - The application runs in containers for easy setup
- **Git** - For downloading the project files
- A text editor (for configuration)
- A web browser (Chrome, Firefox, Safari, or Edge)

## Step 1: Get the Project Files

### Option A: Fork or Clone the Repository (Recommended)

The simplest way to get started is to download the project directly:

1. Open your terminal or command prompt
2. Navigate to the folder where you want to store the project
3. Run this command:

```bash
git clone git@github.com:fastapi/full-stack-fastapi-template.git
```

4. Enter the project folder:

```bash
cd full-stack-fastapi-template
```

### Option B: Create a Private Copy

If you want to keep your version private and make your own changes:

1. Create a new empty repository on GitHub with your desired name (e.g., `my-awesome-project`)
2. Download the template manually:

```bash
git clone git@github.com:fastapi/full-stack-fastapi-template.git my-awesome-project
```

3. Enter your new project folder:

```bash
cd my-awesome-project
```

4. Connect it to your new repository (replace with your GitHub username and repository name):

```bash
git remote set-url origin git@github.com:YOUR-USERNAME/my-awesome-project.git
```

5. Upload the files to your repository:

```bash
git push -u origin master
```

## Step 2: Configure Your Application

The application needs some basic configuration before it can run. You'll need to update a file called `.env` that contains important settings.

### Required Configuration

Open the `.env` file in your text editor and update these three critical values:

1. **SECRET_KEY** - A random password that keeps your application secure
2. **FIRST_SUPERUSER_PASSWORD** - The password for your administrator account
3. **POSTGRES_PASSWORD** - The password for your database

### Generate Secure Keys

For the SECRET_KEY and POSTGRES_PASSWORD, you should use randomly generated values. Generate a secure key by running:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and paste it as the value in your `.env` file. Run the command again to generate a different key for the other field.

### Example Configuration

Your `.env` file should look something like this (with your own values):

```
SECRET_KEY=your_generated_secret_key_here
FIRST_SUPERUSER_PASSWORD=YourStrongPassword123!
POSTGRES_PASSWORD=your_generated_database_password_here
```

### Optional Email Settings

If you want password recovery emails to work, configure these settings (you can skip this for now and add it later):

- **SMTP_HOST** - Your email server address
- **SMTP_USER** - Your email username
- **SMTP_PASSWORD** - Your email password
- **EMAILS_FROM_EMAIL** - The email address to send from

## Step 3: Start the Application

Now you're ready to launch the application!

1. Make sure Docker Desktop is running on your computer
2. In your terminal (inside the project folder), run:

```bash
docker compose up
```

The first time you run this command, it will take several minutes to download and set up everything. You'll see lots of messages in your terminal - this is normal.

### What's Happening Behind the Scenes

When you start the application, several things happen automatically:

- A PostgreSQL database is created and configured
- The database tables and structure are set up
- Your administrator account is created with the email and password you configured
- The backend API server starts
- The frontend dashboard starts
- All services are connected together

Wait until you see messages indicating that all services are healthy and running.

## Step 4: Access Your Application

Once everything is running, you can access your new application:

### Main Dashboard
Open your web browser and go to:
```
http://localhost
```

You should see a login screen.

### Log In for the First Time

Use the administrator credentials you configured:
- **Email**: The value you set for `FIRST_SUPERUSER` (default is `admin@example.com`)
- **Password**: The value you set for `FIRST_SUPERUSER_PASSWORD`

After logging in, you'll see the main dashboard where you can:
- View and manage users
- Create and organize items
- Update your account settings
- Switch between light and dark mode

### API Documentation
To explore the technical API (optional), visit:
```
http://localhost/docs
```

This shows all available API endpoints with interactive documentation.

### Database Management (Optional)
To view and manage your database directly, visit:
```
http://localhost:8080
```

This opens Adminer, a database management tool.

## Verification Steps

Confirm your installation is working correctly:

### ✅ Check 1: Dashboard Loads
- Open `http://localhost` in your browser
- The login page should appear without errors

### ✅ Check 2: Can Log In
- Enter your administrator email and password
- You should successfully log in and see the dashboard

### ✅ Check 3: Can Create Items
- From the dashboard, navigate to the Items section
- Try creating a new item
- The item should save successfully and appear in your list

### ✅ Check 4: Services Are Running
In your terminal where Docker is running, you should see no error messages and all services should show as "healthy"

## Common Setup Issues and Solutions

### Problem: "Variable not set" Error

**Symptom**: When starting Docker, you see errors like `POSTGRES_PASSWORD?Variable not set`

**Solution**: Your `.env` file is missing required values. Make sure you've set all three required variables (SECRET_KEY, FIRST_SUPERUSER_PASSWORD, POSTGRES_PASSWORD) and saved the file.

### Problem: Port Already in Use

**Symptom**: Error message says port 80, 5432, or 8080 is already in use

**Solution**: Another application is using these ports. Either stop the other application, or change the ports in your `docker-compose.yml` file.

### Problem: Can't Connect to Database

**Symptom**: Application starts but shows database connection errors

**Solution**: 
1. Stop the application (press Ctrl+C in the terminal)
2. Remove existing containers: `docker compose down -v`
3. Start again: `docker compose up`

### Problem: Login Not Working

**Symptom**: Correct password doesn't work

**Solution**: 
1. Double-check the email address - it must match exactly what's in your `.env` file
2. Verify you saved the `.env` file after making changes
3. Restart the application to apply the new settings

### Problem: Slow First Startup

**Symptom**: Taking a very long time to start

**Solution**: This is normal for the first run. Docker needs to download several large images (PostgreSQL, the application code, etc.). Subsequent starts will be much faster.

## Stopping the Application

When you're done working:

1. Go to the terminal where Docker is running
2. Press `Ctrl+C` (or `Cmd+C` on Mac)
3. Wait for all services to stop gracefully

To completely remove all containers and data:

```bash
docker compose down -v
```

**Warning**: The `-v` flag deletes your database. Only use this if you want to start completely fresh.

## Next Steps

Now that your application is running:

1. **Explore the Dashboard** - Click around and familiarize yourself with the interface
2. **Create Test Data** - Add some items and see how everything works
3. **Invite Other Users** - Use the user management section to add team members
4. **Customize Your Profile** - Update your account settings and preferences
5. **Try Dark Mode** - Toggle the theme to see the dark mode interface

For daily development work, you only need to run `docker compose up` when you want to start the application, and press `Ctrl+C` when you're done.

## Getting Help

If you encounter issues not covered in this guide:

1. Check that Docker Desktop is running and has enough resources
2. Verify all required values are set in your `.env` file
3. Try stopping everything and starting fresh with `docker compose down -v` then `docker compose up`
4. Review the terminal output for specific error messages
5. Consult the project's GitHub repository for additional documentation

Your local development environment is now ready to use!