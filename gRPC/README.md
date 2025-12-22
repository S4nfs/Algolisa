## Updated Docs

gRPC (gRPC Remote Procedure Calls) is an open source remote procedure call (RPC) system initially developed at Google in 2015. It uses HTTP/2 for transport, Protocol Buffers as the message format.

## Best Features (think about spotify)

- **Language Support**: gRPC supports multiple programming languages including C++, Java, Python, Go, Ruby, C#, Node.js, and more.
- **HTTP/2**: gRPC uses HTTP/2 for transport, which allows for multiplexing multiple requests over a single connection, reducing latency and improving performance.
- **Protocol Buffers**: gRPC uses Protocol Buffers (protobuf) as its interface definition language (IDL) and as its underlying message serialization format, which is efficient and compact.
- **Streaming**: gRPC supports four types of service methods: unary (single request, single response), server streaming (single request, stream of responses), client streaming (stream of requests, single response), and bidirectional streaming (stream of requests and responses). Spotify uses gRPC for its real-time music streaming services.
- **Authentication**: gRPC supports various authentication mechanisms, including SSL/TLS, token-based authentication, and more.
- **Load Balancing**: gRPC has built-in support for load balancing, allowing for better distribution of requests across multiple servers.
- **Cancellation and Timeouts**: gRPC supports cancellation of requests and setting timeouts, which helps in managing long-running operations. So its Statefull rather than REST stateless.
