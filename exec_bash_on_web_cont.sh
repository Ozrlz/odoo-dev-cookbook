docker container exec --user=root -it $(docker container ls | grep web | awk '{ print $NF }') /bin/bash
