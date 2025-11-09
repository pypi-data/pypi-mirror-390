
from typing import List, Self
    
class Contact:
    name: str = ""
    email: str = ""
    country: str = ""
    address: str = ""
    organization: str = ""
    
    def __init__(self: Self, name: str = "", email: str = "", country: str = "", address: str = "", organization: str = ""):
        self.name = name
        self.email = email
        self.country = country
        self.address = address
        self.organization = organization
    
    
class Contacts:
    tech: Contact = None
    owner: Contact = None
    admin: Contact = None
    
    def __init__(self: Self, tech: Contact = None, owner: Contact = None, admin: Contact = None):
        self.tech = tech
        self.owner = owner
        self.admin = admin
    
    
class Registrar:
    url: str = ""
    name: str = ""
    email: str = ""
    
    def __init__(self: Self, url: str = "", name: str = "", email: str = ""):
        self.url = url
        self.name = name
        self.email = email


class Domain:
    ip: str = ""
    name: str = ""
    created: str = ""
    expires: str = ""
    changed: str = ""
    idn_name: str = ""
    ask_whois: str = ""
    contacts: Contacts = None
    registrar: Registrar = None
    name_servers: List[str] = []
    
    def __init__(self: Self, ip: str = "", name: str = "", created: str = "", expires: str = "", changed: str = "", idn_name: str = "",
                 ask_whois: str = "", contacts: Contacts = None, registrar: Registrar = None, name_servers: List[str] = []):
        self.ip = ip
        self.name = name
        self.created = created
        self.expires = expires
        self.changed = changed
        self.idn_name = idn_name
        self.ask_whois = ask_whois
        self.contacts = contacts
        self.registrar = registrar
        self.name_servers = name_servers