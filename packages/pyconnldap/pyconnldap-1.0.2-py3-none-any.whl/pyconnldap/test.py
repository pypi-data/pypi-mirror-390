from connection import Connect


a = Connect()
# b = a.get_user_attrib(username='caminjos', attrib='mail')
# b = a.search_user(username='caminjos', ou=a.USERS_BASE)
# b = a.get_attrib(search='mail=josephus.caminse@teradyne.com', attrib=['cn', 'displayName'])
# b = a.search_in_ou(search='cn=caminjos', ou=a.USERS_BASE)
b = a.search_all_attrib(search='division=BPIT (070)', attrib='cn')
print(b)

