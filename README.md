# Heroku flask boilerplate
 boilerplate code for quick Heroku deployment

 Can also be used for an example.

 Hopefully will save someone a few hours of integration hell.
 
 For your heroku project, 
 
 1. Create an app, make sure to add the python build pack there as well.
 2. go into your project and run `heroku git:remote -a YOUR-APP-NAME`
 3. `git push heroku main`
 4. if it doesnt work, do `heroku ps:scale web=1`
