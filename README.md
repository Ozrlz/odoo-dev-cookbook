# odoo-dev-cookbook
Dev env for for odoo with Docker.

# How to use it
Place a shell inside the folder of the cloned repo and run

  $ docker-compose up
  
Then, go to localhost:8070. If you want to expose another port, change it in the docker-compose.yml (web>ports).

  *        - "8070:8069"
  

## Extra-addons
The extra-addons is mounted in the web container (odoo), so that there you will place your custom addons

