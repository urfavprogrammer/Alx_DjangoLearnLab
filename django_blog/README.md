Django’s authentication leverages  django.contrib.auth  for secure user management, storing credentials in the  auth_user  table with PBKDF2 password hashing. Session middleware tracks logged-in users via  request.user ;  @login_required  decorators protect profile views. Custom  RegisterForm  extends  UserCreationForm  to capture email during signup.
Registration Process
Users visit  /blog/register/ , submit username/email/password via  {{ form.as_p }} . The  register  view validates input, creates  User  instance, saves hashed password, displays success message, and redirects to login. No email verification implemented—extend with signals for production.
Login/Logout Flow
Login ( /blog/login/ ): POST username/password →  authenticate()  checks credentials →  login()  sets session → redirects to  /blog/profile/ .
Logout ( /blog/logout/ ): Calls  logout()  to clear session → redirects to home. CSRF tokens prevent cross-site attacks on all forms.
Profile Management
Authenticated users access  /blog/profile/  to view/edit email. POST updates  user.email  via ORM, flashes success message. Extend by adding  ImageField  bio to custom  UserProfile  model linked via  OneToOneField  for avatars.
Testing Instructions
Run  python manage.py runserver  and test sequentially:
Register : visit /blog/register/, fill form, submit.. it should show a success message, and login redirect

Login: /blog/lgoin, valid credentials: you access the profile page

Logout: Click logout link: redirects to Home_page

security: Access /profile/ unauthenticated: redirects to /blog/login/

## Blog CRUD Features
- List: /posts/ - View all posts
- Create: Authenticated users only, auto-author assignment
- Update/Delete: Author-only via test mixins
- Templates use Bootstrap, forms auto-render with as_p

Add section: “Comments: Auth users post on post detail (/posts//). Authors edit/delete via buttons. Min 10 chars validation. Uses related_name=‘comments’ for post.comments.all().”
