const { ApolloServer } = require("apollo-server");
const { ApolloGateway } = require("@apollo/gateway");
const { RemoteGraphQLDataSource } = require("@apollo/gateway")

class DataSourceWithTimeout extends RemoteGraphQLDataSource {
  willSendRequest({ request }) {
    request.http.timeout = 3000
  }
}
const gateway = new ApolloGateway({
  // This entire `serviceList` is optional when running in managed federation
  // mode, using Apollo Graph Manager as the source of truth.  In production,
  // using a single source of truth to compose a schema is recommended and
  // prevents composition failures at runtime using schema validation using
  // real usage-based metrics.
  serviceList: [
    { name: "user", url: "http://graphql_server_user:8300" },
    { name: "photos", url: "http://graphql_server_photo:8301" },
    { name: "reviews", url: "http://graphql_server_review:8302" },
    { name: "fhir", url: "http://graphql_server_py_fhir:8305" }
  ],
  debug: true,
  buildService: ({ url }) => new RemoteGraphQLDataSource({ url }),
  // Experimental: Enabling this enables the query plan view in Playground.
  __exposeQueryPlanExperimental: false,
});

(async () => {
  const server = new ApolloServer({
    gateway,

    // Apollo Graph Manager (previously known as Apollo Engine)
    // When enabled and an `ENGINE_API_KEY` is set in the environment,
    // provides metrics, schema management and trace reporting.
    engine: false,

    // Subscriptions are unsupported but planned for a future Gateway version.
    subscriptions: false,
  });

  let url = process.env.NODE_URL;
  let port = process.env.PORT;
  server.listen({port: port}).then(({ url }) => {
    console.log(`🚀 Server ready at ${url}`);
  });
})();
