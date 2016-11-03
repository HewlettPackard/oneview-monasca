How to change your python version
=================================


Setup
-----

1. Install  pyenv
```
$ curl -L
https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer
| bash
```

2. edit your bash_profile
```
$ vim .bash_profile
```
  add the following lines
```
# Load pyenv automatically by adding
# the following to ~/.bash_profile:
export PATH="/home/iurygregory/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

3. reload bash_profile
```
$ source .bash_profile
```

4. update  pyenv
```
$ pyenv update
```

5. install thep python version that you want
```
$ pyenv install 2.7.9
```

6. List all pyenv versions
```
$ pyenv versions
* system (set by /home/iurygregory/.pyenv/version)
  2.7.9
```

7. set pyenv to the version that you want
```
$ pyenv global 2.7.9
```

8. verify the choosen version
```
$ pyenv versions
  system
* 2.7.9 (set by /home/iurygregory/.pyenv/version)
```

9. verify your python version
```
$ python --version
Python 2.7.9
```
