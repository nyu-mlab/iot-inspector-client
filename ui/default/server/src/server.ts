import { ApolloServer } from 'apollo-server-express'
import { ApolloServerPluginDrainHttpServer } from 'apollo-server-core'
import * as express from 'express'
import * as path from 'path'
import { createServer } from 'http'
import { makeExecutableSchema } from '@graphql-tools/schema'
import { WebSocketServer } from 'ws'
import { useServer } from 'graphql-ws/lib/use/ws'

import { resolvers, typeDefs } from './schema'
import { context } from './context'

async function startApolloServer(typeDefs, resolvers, context) {
  const app = express()
  const httpServer = createServer(app)

  const schema = makeExecutableSchema({ typeDefs, resolvers })

  // Creating the WebSocket server
  const wsServer = new WebSocketServer({
    // This is the `httpServer` we created in a previous step.
    server: httpServer,
    // Pass a different path here if your ApolloServer serves at
    // a different path.
    path: '/graphql',
  })

  // Hand in the schema we just created and have the
  // WebSocketServer start listening.
  const serverCleanup = useServer({ schema }, wsServer)

  const server = new ApolloServer({
    schema,
    typeDefs,
    context,
    resolvers,
    csrfPrevention: true,
    plugins: [
      // Proper shutdown for the HTTP server.
      ApolloServerPluginDrainHttpServer({ httpServer }),
      // Proper shutdown for the WebSocket server.
      {
        async serverWillStart() {
          return {
            async drainServer() {
              await serverCleanup.dispose()
            },
          }
        },
      },
    ],
  })

  await server.start()
  // ----
  const staticClientPath = path.join(__dirname,'../../html')
  app.use(express.static(staticClientPath)) //serving client side from express
  app.get('*', (req, res) => {
    res.sendFile(`${staticClientPath}/index.html`)
  })
  // --- 
  server.applyMiddleware({ app })
  httpServer.listen({ port: 4000 })

  console.log(`
    🚀 Server ready at: http://localhost:4000${server.graphqlPath}
    ⭐️ See sample queries: http://pris.ly/e/ts/graphql-sdl-first#using-the-graphql-api`)
}

try {
  startApolloServer(typeDefs, resolvers, context)
} catch (e) {
  console.log(e)
}
