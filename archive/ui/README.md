To run Inspector on the local host, simply run

```
./start.bash

```

To set up nginx + streamlit, use the following setup for nginx:

```
server {
       listen 80;
        server_name inspector-demo.public-site.com;

        location / {
                proxy_pass http://IP_ADDRESS:33761/;
                proxy_set_header   Host      $host;
                proxy_set_header   X-Real-IP $remote_addr;
                proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header   X-Forwarded-Proto $scheme;
                proxy_buffering    off;
                proxy_http_version 1.1;
                # Also requires websocket:
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";
                proxy_read_timeout 86400;

        }

        error_log /var/log/nginx/inspector-demo-error.log debug;
        access_log /var/log/nginx/inspector-demo-access.log;


}

```
Sources:
* https://discuss.streamlit.io/t/how-to-use-streamlit-with-nginx/378/7
* https://docs.streamlit.io/knowledge-base/deploy/deploy-streamlit-domain-port-80
