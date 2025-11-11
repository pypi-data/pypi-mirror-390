## Generating or updating `apt_requirements.lock`

On your local system:

```shell
docker build . -f Dockerfile-apt-lock -t apt-lock
docker run -it --rm -v ${PWD}:/media apt-lock
```

The file `apt_requirements.lock` will be generated in the current directory.
