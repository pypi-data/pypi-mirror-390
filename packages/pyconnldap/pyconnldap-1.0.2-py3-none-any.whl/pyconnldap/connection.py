
import ldap3
import subprocess as sp
import os
from dataclasses import dataclass
import platform
from dotenv import load_dotenv
from ldap3.utils.conv import escape_filter_chars


@dataclass
class Connect:
    """
    Handles LDAP connection and authentication setup for Linux and Windows environments.

    This class initializes connection parameters for an LDAP server using either
    simple bind (username/password) or SASL GSSAPI (Kerberos) authentication. It supports
    both direct credential-based logins and Kerberos keytab authentication.

    Environment variables used:
        - LDAP_HOST: LDAP server hostname or IP address
        - LDAP_PORT: LDAP port. Default is 389.
        - LDAP_USER: LDAP username or principal (e.g., user@domain.com)
        - LDAP_PASSWORD: LDAP password for simple authentication
        - LDAP_KEYTAB: Path to the Kerberos keytab file (used for GSSAPI)
        - LDAP_USER_BASE: Optional LDAP base DN for active users
        - LDAP_TERMED_BASE: Optional LDAP base DN for terminated users
        - LDAP_SRV_ACC_BASE: Optional LDAP base DN for service accounts

    Behavior:
        - On Linux:
            * If both `user` and `password` are provided, performs a simple bind.
            * If `keytab` and `user` are provided, performs Kerberos GSSAPI authentication.
        - On Windows:
            * Uses Kerberos GSSAPI authentication automatically.
        - Raises exceptions for missing host, missing credentials, or bind failures.

    Raises:
        ValueError: If LDAP host or credentials are missing.
        RuntimeError: If the operating system is unsupported.
        ConnectionError: If the LDAP bind operation fails.

    Example:
        >>> conn = Connect(host='ldap.example.com', user='jdoe', password='secret')
        >>> # Automatically binds using simple authentication (Linux)
        >>> # or GSSAPI if on Windows and configured properly.
    """
    host: str = None
    port: int = None
    user: str = None
    password: str = None
    keytab: str = None
    
    if platform.system() == 'Windows':
        home_dir = 'HOMEPATH'
    elif platform.system() == 'Linux':
        home_dir = 'HOME'
    else:
        raise RuntimeError(f'Unsupported platform: {platform.system()}')
    
    load_dotenv(os.path.join(os.getenv(home_dir), '.env'))
    
    # Base OU's
    USERS_BASE = os.getenv('LDAP_USER_BASE')
    TERMED_BASE = os.getenv('LDAP_TERMED_BASE')
    SA_BASE = os.getenv('LDAP_SRV_ACC_BASE')

   
    def __post_init__(self) -> None:
        self.host = self.host or os.getenv('LDAP_HOST')
        self.port = self.port or os.getenv('LDAP_PORT')
        self.user = self.user or os.getenv('LDAP_USER')
        self.password = self.password or os.getenv('LDAP_PASSWORD')
        self.keytab = self.keytab or os.getenv('LDAP_KEYTAB')
        
        if not self.host:
            raise ValueError("LDAP host is required (set host or LDAP_HOST environmen variable).")
        if not self.port:
            self.port = 389
        
        if platform.system() == 'Linux':
            if self.user and self.password:
                # Use simple authentication
                server = ldap3.Server(self.host, port=self.port, connect_timeout=10, mode=ldap3.IP_V4_ONLY)
                conn = ldap3.Connection(
                    server,
                    user=self.user,
                    password=self.password,
                    authentication='SIMPLE'
                )
                conn.bind()
            
            elif self.keytab and self.user:
                # Use keytab if avaialable
                sp.getstatusoutput(f'kinit {self.user} -kt {self.keytab}')
                server = ldap3.Server(self.host, port=self.port, connect_timeout=10, mode=ldap3.IP_V4_ONLY)
                conn = ldap3.Connection(
                    server, authentication=ldap3.SASL, sasl_mechanism=ldap3.GSSAPI, receive_timeout=10)
                conn.bind()
            else:
                raise ValueError("Missing credentials: provide either user/password or keytab.")
                
        
        # --- Windows: always use GSSAPI (Kerberos) ---
        elif platform.system() == 'Windows':
            server = ldap3.Server(self.host, port=self.port, connect_timeout=10, mode=ldap3.IP_V4_ONLY)
            conn = ldap3.Connection(
                server, authentication=ldap3.SASL, sasl_mechanism=ldap3.GSSAPI, receive_timeout=10)
            conn.bind()
        
        else:
            raise RuntimeError(f"Unsupported platform: {platform.system()}")
            
        if not conn.bind():
            raise ConnectionError(f"LDAP bind failed: {conn.result}")
        
        self.conn = conn
        

    def search_user(self, username: str, ou: str) -> bool:
        """
        Query username in LDAP.
        Args:
            username (str): username to search
            ou (str): search OU base. e.g. 'cn=users,dc=ter,dc=company,dc=com' or the available variables
                    USERS_BASE, TERMED_BASE, and SA_BASE

        Returns:
            bool: Return True if username exists in OU; False if it doesn't
        Example:
            obj = Connect()
            obj.search_user(username='cn_name', ou=obj.USERS_BASE)
        """
        self.conn.search(f'cn={username},{ou}',
                        '(objectclass=person)')
        return bool(self.conn.entries)
    
    
    def search_in_ou(self, search: str, ou: str) -> bool:
        """
        Search an attribute=value pair in LDAP and return True if exists in OU else False.
        
        Args:
            username (str): username to search
            ou (str): search OU base. e.g. 'cn=users,dc=ter,dc=company,dc=com' or the available variables
                    USERS_BASE, TERMED_BASE, and SA_BASE

        Returns:
            bool: Return True if username exists in OU; False if it doesn't
            
        Example: user_in_ou(search='mail=first.last@company.com', ou=self.USERS_BASE)
        Example: user_in_ou(search='cn=uniquecn', ou=self.TERMED_BASE)
        """
        self.conn.search(f'{ou}',
                        f'({search})')
        return bool(self.conn.entries)
    
    
    def get_user_attrib(self, username: str, attrib: str|list=None, ou: str=None) -> dict:
        """
        Get user's attributes in AD such as mail, displayName, department, l, etc.
        
        Args:
            username (str): user cn. 
            attrib (str | list, optional): Attributes to return. Defaults to all(*).
            ou (str, optional): OU search base. Defaults to USERS_BASE(active OU).

        Returns: attributes in dictionary format. Eg.: {'cn': 'username', 'userAccountControl': 512}
        
        Example: get_user_attrib(username='username')  
        Example: get_user_attrib(username='username', attrib='mail')
        Example: get_user_attrib(username='username', attrib=['mail', 'displayName'])
        """
        if ou is None:
            ou = self.USERS_BASE    # default
        if ou is None:  # if still not set.
            raise ValueError(f'OU is required. Current value is {ou}')    
        
        if attrib is None:  # default all
            attrib_list = ['*']
        else:
            attrib_list = attrib
            
        self.conn.search(f'cn={username},{ou}',
                '(objectclass=person)', 
                attributes=attrib_list)
        try:
            return self.conn.response[0]['attributes']
        except IndexError:
            # No entries from OU
            return None
            
    
    
    def get_attrib(self, search: str, attrib: str|list=None, ou: str=None) -> dict:
        """
        Search a user account based on attribute=value key pair and return the attributes.
        This works best for a specific attributes to the user like mail or cn 
        
        Args:
            search (str): Attributes=value search keyword. 
            attrib (str | list, optional): Attributes to return. Defaults to all(*).
            ou (str, optional): OU search base. Defaults to USERS_BASE(active OU).

        Returns: attributes in dictionary format.
        
        Example: get_attrib(search='mail=fist.last@company.com')
        Example: get_attrib(search='mail=fist.last@company.com', attrib='cn')
        Example: get_attrib(search='mail=fist.last@company.com', attrib=['cn', 'displayName'])
        """
        if ou is None:
            ou = self.USERS_BASE    # default
        if ou is None: # if still not set.
            raise ValueError(f'OU is required. Current value is {ou}')
            
        if attrib is None:  # default all
            attrib_list = ['*']
        else:
            attrib_list = attrib
            
        self.conn.search(f'{ou}',
                f'({search})', 
                attributes=attrib_list)
        
        try:
            return self.conn.response[0]['attributes']
        except IndexError:
            # No entries from OU
            return None
        
    
    def search_all_attrib(self, search: str, attrib: str|list=None, ou: str=None) -> list:
        """
        Search a users based on "attribute=value" key pair and return all the matches.
        Use when search query is expected to return multiple values like "division=BPIT (070)". 
        
        Args:
            search (str): Attributes=value search keyword. 
            attrib (str | list, optional): Attributes to return. Defaults to all(*).
            ou (str, optional): OU search base. Defaults to USERS_BASE(active OU).

        Returns: 
            All matching attributes in list format.
        
        Example: 
            search_all_attrib(search='division=BPIT (070)', attrib='cn')
       
        """
        if ou is None:
            ou = self.USERS_BASE    # default
        if ou is None: # if still not set.
            raise ValueError(f'OU is required. Current value is {ou}')
            
        if attrib is None:  # default all
            attrib_list = ['*']
        else:
            attrib_list = attrib
            
        search = escape_filter_chars(search)
        self.conn.search(f'{ou}',
                f'({search})', 
                attributes=attrib_list)
        
        try:
            return [entry['attributes'] for entry in self.conn.response]
        except IndexError:
            # No entries from OU
            return None
        