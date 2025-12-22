const grpc = require('@grpc/grpc-js')
const protoLoader = require('@grpc/proto-loader')

const PROTO_PATH = __dirname + '/todo.proto'
const packageDef = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
})
const grpcObject = grpc.loadPackageDefinition(packageDef)
const todoPackage = grpcObject.todoPackage

const client = new todoPackage.Todo('localhost:4000', grpc.credentials.createInsecure())
//////////
client.createTodo(
  {
    id: -1,
    text: 'Build something that people want',
  },
  (err, response) => {
    if (err) {
      console.error('createTodo error:', err)
      return
    }
    console.log('createTodo response:', response)
  }
)
///////////
client.readTodos({}, (err, response) => {
  if (err) {
    console.error('readTodos error:', err)
    return
  }
  if (!response.items) {
    console.log('readTodos response:', response)
  }
})
//////////
const call = client.readTodosStream()
call.on('data', (item) => {
  console.log('STREAMING--', item)
})

call.on('end', (e) => console.log('DONE!'))
