import imaplib
import gmail_imap

class gmail_mailboxes:
    
    def __init__(self, gmail_server):
        self.server = gmail_server
        self.mailboxes = list()

        
    def load(self):
        if(not self.server.loggedIn):
            self.server.login()
        
        for box in self.server.imap_server.list()[1]:
            name = box.split(' "/" ')[1][1:-1]
            if( name != "[Gmail]"):  #ignore global [Gmail] mailbox
                self.mailboxes.append(name)
                   
                   
    def __repr__(self):
        return "<gmail_mailboxes:  [%s]>" %  (',  '.join(self.mailboxes))
        
    def __getitem__(self, key): return self.mailboxes[key]
    def __setitem__(self, key, item): self.mailboxes[key] = item