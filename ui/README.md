This directory includes all the front-end user interface (UI) code.

The front-end UI interacts with the Inspector daemon through a RESTful API,
defined in `apiserver.py`. To view the documentation, run Inspector and navigate
to http://127.0.0.1:53721/redoc or http://localhost:53721/docs. For details,
refer to the main README file at the root of the repository, run Inspector.

By default, when Inspector runs, it will open the webpage at
`ui/default/html/index.html`. This is the `default` UI.

Users have the freedom to load alternative UIs. As a hypothetical example, users
can load a cat-themed UI by downloading the UI's code into the `ui/cat`
directory. The cat-themed UI should have the main page at
`ui/cat/html/index.html`. The user would have to change Inspector's
configuration file to switch the UI from `default` to `cat`. Note: This feature
is currently not implemented.