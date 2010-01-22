import imaplib
import gmail_mailboxes, gmail_messages, gmail_message

class gmail_imap:

    def __init__ (self, username, password):
        self.imap_server = imaplib.IMAP4_SSL("imap.gmail.com",993)
        self.username = username
        self.password = password
        self.loggedIn = False
        
        self.mailboxes = gmail_mailboxes.gmail_mailboxes(self)
        self.messages = gmail_messages.gmail_messages(self)
        
    def login (self):
        self.imap_server.login(self.username,self.password)
        self.loggedIn = True
    
    def logout (self):
        self.imap_server.close()
        self.imap_server.logout()
        self.loggedIn = False
        

        
if __name__ == '__main__':        

    gmail = gmail_imap("email","password")
    
    gmail.mailboxes.load()
    print gmail.mailboxes
    
    gmail.messages.process("INBOX")
    print gmail.messages
  
    for msg in gmail.messages[0:2]:
      message = gmail.messages.getMessage(msg.uid)
      print message
    
    gmail.logout()