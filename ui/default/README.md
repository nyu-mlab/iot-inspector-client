
## Commands
### Setup
From within `ui/default` directory
```bash
yarn install:all  # This will install dependencies within server and client
yarn prisma:generate  # This will compile a prisma server for your OS/architecture.
```

If this is your first time running the app, spin up the database so that we have it in place. Note this will spin it up and run it, you'll need to run this in a separate terminal window
```bash
yarn mockdb
```

### Running the App
Spin both the client and graphql server up. Note this should be run within the `ui/default` directory. It will concurrently run both client and server.
```bash
yarn dev
```

Within another tab (if not already running), to run the mock database (which needs to be run when running the app) run:
```bash
yarn mockdb
```

This will run the mock database and generate database files.

### Building the App
From within `ui/default` run:
```bash
yarn client:build
```

This will output a distribution to: `ui/default/html`

*NOTE: If you're running ngrok, the server also looks at this directory and feeds it as a static directory.*

### Cleaning the App
To remove all node modules
```bash'
yarn clean:all
```

To Remove the database files
```bash
yarn clean:db
```

### Other commands
Note: Be cautious running these, make sure you know/understand what they do before running them.
```bash
# introspect your database. Note that this will populate your Prisma schema file with Prisma models that represent your database schema:
npx prisma introspect

npx prisma generate

npx prisma studio
```

## FAQs
- Whats the difference between `app/` and `server/`
  - `app/` is the client application that will run on port 3000
  - `server/` is the graphql server that will run on port 4000
- Whats the Python Mock Database?
  - Generates mock data that the graphql server uses
- Where do I install node dependencies?
  - If they're for the client, change directories to `app/` and install within there
  - If they're for the server, change directories to `server/` and install within there
