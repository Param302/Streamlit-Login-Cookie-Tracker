# # Function to register a new user
# def register_user(email, password):
#     try:
#         user = auth.create_user(email=email, password=password)
#         st.success(f"User {user.email} created successfully!")
#     except Exception as e:
#         st.error(f"Error: {e}")

# # Function to login a user
# def login_user(email, password):
#     try:
#         user = auth.get_user_by_email(email)
#         st.session_state['user_id'] = user.uid
#         st.session_state['user_email'] = user.email
#         st.success(f"Welcome {user.email}")
#         return user
#     except Exception as e:
#         st.error(f"Error logging in: {e}")
#         return None



# if 'user_id' in st.session_state:
#     st.sidebar.title("Expense Tracker")
#     st.sidebar.write(f"Logged in as {st.session_state['user_email']}")

#     # Daily Expense Tracker
#     st.subheader("Add Today's Expense")
#     expense_name = st.text_input("Expense Name")
#     expense_price = st.number_input("Expense Price", min_value=0.0, format="%.2f")

#     if st.button("Add Expense"):
#         if expense_name and expense_price >= 0:
#             ...
#             # add_expense(st.session_state['user_id'], expense_name, expense_price)
#         else:
#             st.error("Please enter valid expense details.")

#     st.subheader("Today's Expenses")
#     # get_todays_expenses(st.session_state['user_id'])

#     st.subheader("Previous Expenses")
#     # get_previous_expenses(st.session_state['user_id'])

# else:
#     # User Authentication
#     st.sidebar.title("Login / Register")

#     option = st.sidebar.selectbox("Choose action", ["Login", "Register"])

#     email = st.text_input("Email")
#     password = st.text_input("Password", type="password")

#     if option == "Register":
#         if st.button("Register"):
#             if email and password:
#                 register_user(email, password)
#             else:
#                 st.error("Please enter email and password.")

#     elif option == "Login":
#         if st.button("Login"):
#             if email and password:
#                 login_user(email, password)
#             else:
#                 st.error("Please enter email and password.")
