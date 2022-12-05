# CSCD58 Final Project - Client Server Chat Room

For my final project, I created a chat room application using my attempt at an implementation of the XMP Protocol. The repo includes two version of the project. One with encryption and one without. This was done in order to show how easy it would be for an outside party to intercept these packets and see what was being sent to and from the server. 

## Goals

- [x] Client and Server Application
- [x] Show how someone can intercept the packets (Wireshark demo?)
- [x] Encryption

## How to Run

### Server

```bash
cd server
pip install -r requirements.txt
python ./server.py
```

or using Docker

```bash
cd server
docker build --tag cscd58-server .
docker run cscd58-server
```

### Client

**NOTE**: The UI of the client application uses PyQt6. Make sure this is installed on your machine. There seems to be issues with installing PyQt6 on M1.

```bash
cd client
pip install -r requirements.txt
python ./client.py jackie localhost
```

## Implementation

### XMPP

After doing some research, I learned that one of the most popular protocols used in messaging apps is the Extensible Messaging and Presence Protocl (XMPP). 

- Jabber ID (JID)
  - jackie@cscd58.utoronto.ca/desktop
  - local part defines the account on the server
  - domain part defines the server we are connecting to
  - local@domain is called the bare JID
  - resource part defines the specific client (desktop, phone...)
- Streams
  - There are two streams for each TCP socket. Input and output. In my implementation the data sent to and from the XMPP entities are handled as two streams but there is not distinction in the code. If we wanted, we could store the XML into "files" and therefore we would now have 2 distinct streams, but this could lead to some problems. For lots of connections, there would be a lot of data to store.
  - When the client connects to the server, it will send a request to the server to start the stream

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

  - Server will resopond and start another stream
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

  - When the client wants to exit, it will send the following XML to close the stream and end the connection
  ```xml
  <stream:stream />
  ```
- Stanzas
  - Stanzas are units of structured information that are sent over the XML stream. There are 3 basic stanzas needed for a simple XMPP implemenation are `<message />`, `<iq />`, `<prescence />`. In my implementation, I only required `<message />` and `<prescence />`, though there were some features that could have used the `<iq />` stanza to fetch information such as getting list of online users.

My XMPP implementation is stored in the `xmpp.py`. There I have created 3 classes. `XMPPEntity` which is an abstraction of a XMPP Entity and contains the basic methods required for any XMPP Entity. `XMPPServer` which contains the server logic of an XMPP Server. `XMPPClient` which contains the client logic and implmentation. 

Since the client and server need to send and recieve data at the same time, both `XMPPServer` and `XMPPClient` use multithreading in there implementation. On the client side, the main thread will run the UI as well as handle sending the data on the XML Stream. On the server side, the main thread will be listening for connections and create a new thread to handle each connection.

### Security/Encryption

After XMPP has opened the streams, the server will then send `<features/>` elements that are features that get negotiated on the stream. These features include TLS, authentication and compression. In some cases, the features will require a stream restart. This means that both streams will need to be replaced but not close the underlying TCP connection.

In my implmentation, TLS can already be established before the stream opens to ensure security and encryption so these features steps are not required. Using python's `ssl` library we can wrap a socket in a SSL Context.

## Limitations of My Implementation

I tried my best to follow the specifications of the XMPP and although the chat room does work, there are some limitations. 

- Large XML elements can break the server
  - Since the server and client will only recieve 1024 bytes of data each time, it could be the case that an XML element being sent could exceed 1024 bytes in size. In this case, only part of the XML data is sent in the stream and the server and client won't be able to parse it properly. For example, to get the list of online users, the server will send a message stanza for each online user to the connecting client (ideally this would be done with a iq stanza). If the number of online users is too large, the client may not be able to parse all the data properly. A possible fix to this would be to create a custom recv function that will constantly accept data from the socket until we have valid XML data and then return it so we can parse.
- Lack of error handling
  - There is little error handling in my implementation. Users could pass bad XML data and it would cause the program to exit. Ideally, we would send XML error elements to the stream but since I have made sure that the data being sent is proper XML, it wasn't an issue in this project. But, this is definitley something that needs to be implemented in the future.


## Conclusion

Building a protocol is hard. There are a lot of things that you need to consider in order to have a working end-to-end protocol. 
- concluding remarks, lessons learned.
- thought it was going to be easy but later learned about the different protocols
- specifications were very detailed
- learned about XMPP popular