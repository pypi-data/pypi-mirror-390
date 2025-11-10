from connection import Connect


# c = Connect(user='RON_DALLAS/teradyne',
#             host='app-eng-vip.corp.teradyne.com',
#             port='2600',
#             db='csdbAPP.corp.teradyne.com')

c = Connect()

# a = c.get_all_rows(column_name='name')
a = c.get_user_info(user_name='caminjos', column_name='name')
print(a)