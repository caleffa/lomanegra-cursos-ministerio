## TODO
Actualizar el README

## Instalación VMs para Atenea

En este repositorio se encuentran los scripts necesarios para instalar y configurar las VMs que se vayan a usar para los distintos entornos de Atenea.

Utilizamos Ansible para escribir una receta que se puede ejecutar sobre cualquier VM con **Ubuntu 18.04**.

Ansible es una herramienta que se lanza desde la PC del administrador que va a configurar la VM. Se debe instalar localmente (y no en la VM), y al ejecutar el "playbook" Ansible se conecta a la VM para realizar las modificaciones necesarias.

Para la instalación de Ansible los remitimos [al manual oficial](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html). Aquí usamos la versión 2.8, pero en general cualquier versión >= a la 2.5 debería funcionar correctamente.

Una vez instalado Ansible, debemos tener configurado el cliente SSH para poder conectarnos a la VM que queremos configurar con su hostname. Por ejemplo, yo tengo las siguientes líneas en mi archivo `~/.ssh/config`:

    Host geohogar-prod
    Hostname 186.122.147.187
    Port    10422
    User    interinnovacion


Uds. deberían tener algo similar para la VM de qa.


Para verificar que podemos conectarnos a la VM con ansible, ejecutar:

    ansible geohogar-qa -m ping

En caso de ejecución exitosa, veremos en la pantalla el siguiente output:

    geohogar-qa | SUCCESS => {
      "changed": false,
      "ping": "pong"
    }


Para ejecutar la receta, corremos el siguiente comando:

    ansible-playbook -K geohogar-backend.yml -l geohogar-qa


Por último, debemos ejecutar en la VM el siguiente comando para registrar Gitlab Runner:

    sudo gitlab-runner register

Es un script interactivo que nos irá haciendo varias preguntas. Estas son las respuestas:

- coordinator URL: https://gitlab.com/
- token: (lo enviaremos por email)
- tags: qa (en producción, sería 'production')
- executor: shell

El output se ve así:

    Runtime platform                                    arch=amd64 os=linux pid=1610 revision=a8a019e0 version=12.3.0
    Running in system-mode.

    Please enter the gitlab-ci coordinator URL (e.g. https://gitlab.com/):
    https://gitlab.com/
    Please enter the gitlab-ci token for this runner:
    **************
    Please enter the gitlab-ci description for this runner:
    [qa-test]:
    Please enter the gitlab-ci tags for this runner (comma separated):
    qa
    Registering runner... succeeded                     runner=g5jzoQKT
    Please enter the executor: parallels, ssh, docker-ssh+machine, kubernetes, custom, docker, docker-ssh, shell, virtualbox, docker+machine:
    shell
    Runner registered successfully. Feel free to start it, but if it's running already the config should be automatically reloaded!


Eso es todo.