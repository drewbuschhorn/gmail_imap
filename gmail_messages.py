import email, string, rfc822, re
from email.parser import HeaderParser
import gmail_imap,gmail_mailboxes,gmail_message

class gmail_messages:
    
    def __init__(self, gmail_server):
        self.server = gmail_server
        self.mailbox = None
        self.messages = list()
    
    def parseFlags(self, flags):
        return flags.split()
    
    def parseMetadata(self, entry):
        if(not getattr(self,'metadataExtracter',False) ):
            self.metadataExtracter = re.compile(r'(?P<id>\d*) \(UID (?P<uid>\d*) FLAGS \((?P<flags>.*)\)\s')  
            #  I hate regexps.  (\d*) = MSG ID
            #  \(UID (\d*) = MSG UID
            #  FLAGS \((.*)\)\s = MSG FLAGS, may be empty
                    #example:  55 (UID 82 FLAGS (\Seen) BODY[HEADER.FIELDS (SUBJECT FROM)] {65}
                    #               groupdict() = { id:'55', uid:'82', flags:'\\Seen' }        
        metadata = self.metadataExtracter.match(entry).groupdict();
        metadata['flags'] = self.parseFlags(metadata['flags'])
        return metadata
    
    def parseHeaders(self,entry):
        if(not getattr(self,'headerParser',False) ):
            self.headerParser = HeaderParser()
        
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
        fetch_list = string.split(data[0])[-10:]# limit to 100 most recent mails in mailbox
        fetch_list = ','.join(fetch_list)
        
        if(fetch_list):
            f = self.server.imap_server.fetch(fetch_list, '(UID FLAGS BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])')
            for fm in f[1]:
                if(len(fm)>1):
                    metadata = self.parseMetadata(fm[0])
                    headers = self.parseHeaders(fm[1])
                    
                    message = gmail_message.gmail_message()
                    message.id = metadata['id']
                    message.uid = metadata['uid']
                    message.flags = metadata['flags']
                    message.mailbox = mailbox  #UID depends on mailbox location
        
                    message.date = headers['Date']
                    message.From = headers['From']
                    if( 'Subject' in headers ):
                        message.Subject = headers['Subject']
                        
                    self.messages.append(message)
                    
                    
    def __repr__(self):
        return "<gmail_messages:  \n%s\n>" %  (self.messages)