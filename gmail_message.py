import email,string
import gmail_imap

class gmail_message:

    def __init__(self):
    
        self.id = None
        self.uid = None
        self.flags = None
        self.mailbox = None
        self.date = None
        
        self.From = None
        self.Subject = '( no subject )'
        self.Body = None
        
    def __repr__(self):
        str = "<gmail_message:  ID: %s  UID: %s Flags: %s Date: %s \n" % (self.id,self.uid,self.flags,self.date)
        str += "from: %s subject: %s >" % (self.From,self.Subject)
        return str
        
    def getMessage(self, server, mailbox, uid):
        if(not server.loggedIn):
            server.login()
        server.imap_server.select(mailbox)
        
        status, data = server.imap_server.uid('fetch',uid, 'RFC822')
        messagePlainText = ''
        messageHTML = ''
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_string(response_part[1])
                for part in msg.walk():
                    if str(part.get_content_type()) == 'text/plain':
                        messagePlainText = messagePlainText + str(part.get_payload())
                    if str(part.get_content_type()) == 'text/html':
                        messageHTML = messageHTML + str(part.get_payload())
        
        
        #create new message object
        message = gmail_message()
        
        if(messageHTML != '' ):
            message.Body = messageHTML
        else:
            message.Body = messagePlainText
        if('Subject' in msg):
            message.Subject = msg['Subject']
        message.From = msg['From']
        
        message.uid = uid
        message.mailbox = mailbox
        message.date = msg['Date']
        
        return message