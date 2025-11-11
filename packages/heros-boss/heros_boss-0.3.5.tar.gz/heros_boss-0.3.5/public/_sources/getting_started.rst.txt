Getting Started
===============


Possible Configuration Sources
++++++++++++++++++++++++++++++

Device configuration data can be supplied to BOSS from various sources.

.. tabs::

   .. tab:: Network based JSON Database

      For a production setup, we recommend using a network based database like CouchDB. This has the advantage, that
      all configurations are at a central point and are easy to maintain.

      .. code-block:: bash

         python -m boss.starter -u http://<user>:<pw>@<couchdb_host>:5984/my-boss/http-test

      See :ref:`CouchDB <couchdb-head>` for more details.


   .. tab:: JSON File

      For testing purposes or isolated BOSS instances, you can also directly supply a :ref:`JSON file <json-head>`
      with the device configuration inside. Run BOSS with the *absolute path* to the JSON file:

      .. code-block:: bash

         python -m boss.starter --u file:///absolute/path/to/file.json




   .. tab:: Environment Variables

      BOSS can also load the configuration from environment variables

      .. code-block:: bash

          export BOSS1={"_id": "docker-env-ftp","classname": "ftplib.FTP","arguments": {"host": "ftp.us.debian.org"}}
          python -m boss.starter -e BOSS1

      This can make sense for example for docker based portable deployments. An example of this can be found in the
      Docker :ref:`compose file below <start-compose>`.


.. hint::

   BOSS uses *urllib* to parse the url specified by the ``-u`` argument, which supports many more `url schemes <https://docs.python.org/3/library/urllib.parse.html>`_ than listed here.
   This means you can use also completely different endpoints to host your configuration for BOSS like `ftp` or `svn`, the only requirement
   is that there is a valid JSON configuration string at the end.

Installing/Deploying BOSS
+++++++++++++++++++++++++

.. tabs::


    .. _start-compose:
    .. tab:: Docker Compose

        A convenient way to deploy BOSS is inside of a docker container. You can find pre-build containers images in
        our docker `registry <https://gitlab.com/atomiq-project/boss/container_registry>`_.


        .. hint::

           You can also build the BOSS docker image yourself from the Dockerfile in the repository:
           ``docker build -t atomiq/boss .``
           By building the docker image yourself, you can `modify the docker image <https://docs.docker.com/build/building/base-images/>`_
           and add for example custom device vendor libraries or similar.


        A BOSS docker service can be started with the following compose file

        .. code-block:: yaml

            services:
              httpclient:
                image: registry.gitlab.com/atomiq-project/boss:latest
                restart: always
                network_mode: host
                environment:
                 - |
                   BOSS1=
                   {
                    "_id": "docker-env-ftp",
                       "classname": "ftplib.FTP",
                       "arguments": {
                            "host": "ftp.us.debian.org"
                       }
                   }
                command: python -m boss.starter -e BOSS1

        Additionally, also specifying a file or URL is possible, such that (mounted) json files in the docker container or web
        URLs can be used as configuration sources. Note that the ``-e`` and ``-u`` options can be specified in the command line
        multiple times to define several objects that should be instantiated by the BOSS.

    .. tab:: Local Installation

        BOSS can also be installed locally via pip:

        .. hint::

           We recommend using `uv <https://docs.astral.sh/uv/>`_ to maintain an enclosed python environment.

        .. tabs::

           .. tab:: uv

              .. code-block::

                 uv pip install heros-boss


           .. tab:: other

              .. code-block::

                 pip install heros-boss


        Now you are ready to go! You can get an overview over the command line arguments of boss by running

        .. tabs::

           .. tab:: uv

              .. code-block::

                 uv run python -m boss.starter --help


           .. tab:: other

              .. code-block::

                 python -m boss.starter --help




