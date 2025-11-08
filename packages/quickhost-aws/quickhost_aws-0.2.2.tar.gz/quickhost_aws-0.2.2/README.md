# quickhost plugins

The AWS plugin for [quickhost](https://github.com/zeebrow/quickhost) - start your hosts in AWS
quickly. No state or configuration required!

Test coverage is 79%

## Suggested - use `pipx`

[pipx](https://github.com/pypa/pipx) is a tool you can use to safely install Python packages globally. It is the recommended way to install quickhost and its plugins.

Install:

```
pipx install quickhost
pipx inject quickhost quickhost-aws
```

### Usage

NOTE!
The `--region` parameter is not fully supported! Only use it with `init`!
DO NOT USE IT!

```
# set up aws credentials and essential resources in aws
# this creates a user named "quickhost-user," which will be responsible for any quickhost actions.
# The region supplied is where hosts will run, unless specified otherwise
quickhost -vvv aws init --admin-profile define-admin --region us-east-1

# you have nothing running yet
quickhost -vvv aws list-all

# start a linux host
quickhost -vvv aws make my_app

# see that your host is running
quickhost -vvv aws list-all

# permanently get rid of what you made above
quickhost -vvv aws destroy my_app

# permanently get rid of aws resources made by quickhost including any apps still running
quickhost -vvv aws plugin-destroy

```

