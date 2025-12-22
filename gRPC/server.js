const grpc = require('@grpc/grpc-js')
const protoLoader = require('@grpc/proto-loader')

const PROTO_PATH = __dirname + '/todo.proto'

// Load proto with recommended options for grpc-js
const packageDef = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
})
const grpcObject = grpc.loadPackageDefinition(packageDef)
const todoPackage = grpcObject.todoPackage

// In-memory store for demo
const todos = []

function createTodo(call, callback) {
  // console.log('CALL_PAYLOAD::::', call)
  const item = {
    id: todos.length + 1,
    text: call.request.text,
  }
  todos.push(item)
  callback(null, item)
}

function readTodos(call, callback) {
  callback(null, { items: todos })
}

function readTodosStream(call, callback) {
  todos.forEach((i) => call.write(i))
  call.end()
}

const server = new grpc.Server()

server.addService(todoPackage.Todo.service, {
  createTodo,
  readTodos,
  readTodosStream,
})

server.bindAsync('localhost:4000', grpc.ServerCredentials.createInsecure(), (err, port) => {
  if (err) {
    console.error('Server bind error:', err)
    return
  }
  console.log(`gRPC server listening on ${port}`)
  server.start()
})
