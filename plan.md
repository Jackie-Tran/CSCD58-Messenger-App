# Messenger App Plan

Types of communication:
- Peer to peer
- Group chats

Plan
- [x] Create client and server applications
- [x] Test sending data over socket
- [ ] Implement a variation of the XMPP protocol
  - [ ] Open send and recieve xml streams
  - [ ] Handle message, presence, iq stanzas
- [ ] Demo to show how packets can be intercepted
- [ ] Implement security/encryption


## Custom XMPP Protocol
- Jabber ID (JID)
  - jackie@cscd58.utoronto.ca/desktop
  - local part defines the account on the server
  - domain part defines the server we are connecting to
  - local@domain is called the bare JID
  - resource part defines the specific client (desktop, phone...)
- Streams
  - two streams, input and output over one TCP socket
  - streams will restart when there is a state change (TLS or stream compression)
- Client connects to server and starts a stream
```xml
<?xml version='1.0'?>
      <stream:stream
          from='juliet@im.example.com'
          to='im.example.com'
          version='1.0'
          xml:lang='en'
          xmlns='jabber:client'
          xmlns:stream='http://etherx.jabber.org/streams'>
```
- Server will respond and start another stream
```xml
<?xml version='1.0'?>
      <stream:stream
          from='im.example.com'
          id='++TR84Sm6A3hnt3Q065SnAbbk3Y='
          to='juliet@im.example.com'
          version='1.0'
          xml:lang='en'
          xmlns='jabber:client'
          xmlns:stream='http://etherx.jabber.org/streams'>
```
- Server then sends a list of features (authentication, tls)
- These features will update the state of the stream so we restart a new stream
- Stanza
  - an XML element which acts as a basic unit in XMPP
  - `<message />`
    - attr from: the JID of the sender
    - attr to: the JID of the intended recipient
    - attr xml:lang: language
    - attr type: type of message
    - body: message content
  - `<iq />`
  - `<prescence />`