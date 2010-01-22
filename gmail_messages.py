import email, string, re
from email.parser import HeaderParser
import gmail_imap,gmail_mailboxes,gmail_message

class gmail_messages:
    
    def __init__(self, gmail_server):
        self.server = gmail_server
        self.mailbox = None
        self.messages = list()
    
    def parseFlags(self, flags):
        return flags.split()  # Note that we don't remove the '\' from flags, just split by space
    
    def parseMetadata(self, entry):
        if(not getattr(self,'metadataExtracter',False) ):   #Lazy initiation of the parser
            self.metadataExtracter = re.compile(r'(?P<id>\d*) \(UID (?P<uid>\d*) FLAGS \((?P<flags>.*)\)\s')  
            #  I hate regexps.
            #  (\d*) = MSG ID,  the position index of the message in its mailbox
            #  \(UID (\d*) = MSG UID, the unique id of this message within its mailbox
            #  FLAGS \((.*)\)\s = MSG FLAGS, special indicators like (\Starred, \Seen) may be empty
                    #example:  55 (UID 82 FLAGS (\Seen) BODY[HEADER.FIELDS (SUBJECT FROM)] {65}
                    #               groupdict() = { id:'55', uid:'82', flags:'\\Seen' }        
        
        metadata = self.metadataExtracter.match(entry).groupdict() 
        metadata['flags'] = self.parseFlags(metadata['flags'])
        return metadata
    
    def parseHeaders(self,entry):
        if(not getattr(self,'headerParser',False) ):
            self.headerParser = HeaderParser()  #See http://docs.python.org/library/email.parser.html#parser-class-api
        
        headers = self.headerParser.parsestr(entry)
        return headers
    
    def process(self,mailbox):
        self.mailbox = mailbox
        self.messages = list()
        
        if(not self.server.loggedIn):
            self.server.login()
        
        result, message = self.server.imap_server.select(mailbox,readonly=1)
        if result != 'OK':
            raise Exception, message
        typ, data = self.server.imap_server.search(None, '(UNDELETED)')
        fetch_list = string.split(data[0])[-10:]# limit to N most recent messages in mailbox, this is where pagination should be implemented
        fetch_list = ','.join(fetch_list)
        
        if(fetch_list):
            f = self.server.imap_server.fetch(fetch_list, '(UID FLAGS BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])')
            for fm in f[1]:
                if(len(fm)>1):
                    metadata = self.parseMetadata(fm[0]) #metadata is contained 
                    headers = self.parseHeaders(fm[1])
                    
                    message = gmail_message.gmail_message()
                    message.id = metadata['id']
                    message.uid = metadata['uid']
                    message.flags = metadata['flags']
                    message.mailbox = mailbox   #UID depends on mailbox location so,
                                                                #we need to know which owns the message
        
                    message.date = headers['Date']
                    message.From = headers['From']
                    if( 'Subject' in headers ):
                        message.Subject = headers['Subject']
                        
                    self.messages.append(message)
                    
                    
    def __repr__(self):
        return "<gmail_messages:  \n%s\n>" %  (self.messages)
    
    def __getitem__(self, key): return self.messages[key]
    def __setitem__(self, key, item): self.messages[key] = item
    
    def getMessage(self, uid):
        if(not self.server.loggedIn):
            self.server.login()
        self.server.imap_server.select(self.mailbox)
        
        status, data = self.server.imap_server.uid('fetch',uid, 'RFC822')
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
        message = gmail_message.gmail_message()
        
        if(messageHTML != '' ):
            message.Body = messageHTML
        else:
            message.Body = messagePlainText
        if('Subject' in msg):
            message.Subject = msg['Subject']
        message.From = msg['From']
        
        message.uid = uid
        message.mailbox = self.mailbox
        message.date = msg['Date']
        
        return message