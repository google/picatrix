# Setting up Your Development Environment

This guide is to help you set up your development environment for picatrix.

The general flow is:

1. Fork the project into your personal account
2. Grab a copy of the personal fork to your machine (git clone)
3. Create a feature branch on the personal fork
4. Work on your code, commit the code to the feature branch
5. Push the feature branch to your personal fork
6. Create a pull request (PR) on the main project.

## Setting up Git

Start by visiting the [project](https://github.com/google/picatrix) and click the `Fork` 
button in the upper right corner of the project to fork the project into your personal
account.

Once the project has been forked you need to clone the personal fork and add the upstream project.

```shell
$ git clone https://github.com/<USERAME>/picatrix.git
$ cd picatrix
$ git remote add upstream https://github.com/google/picatrix.git
```

You also need to make sure that git is correctly configured

```shell
$ git config --global user.name "Full Name"
$ git config --global user.email name@example.com
$ git config --global push.default matching
```

Next is to make sure that `.netrc` is configured. For more information see: https://gist.github.com/technoweenie/1072829

## Create a Feature Branch

Every code change is stored in a separate feature branch:

### Sync Main Branch

Make sure the master branch of your fork is synced with upstream:

```shell
$ git checkout main
$ git fetch upstream
$ git rebase upstream/main
$ git push
```

or in a single command:
```shell
$ git checkout main && git fetch upstream && git rebase upstream/main && git push
```

### Create a feature branch:

```shell
$ git checkout -b <NAME_OF_BRANC>
```

eg:

```shell
$ git checkout -b my_awesome_feature
```

Make the necessary code changes, commit them to your feature branch and upload them to your fork:

```shell
$ git push origin <NAME_OF_BRANCH>
```

## Make Changes

Make your changes to the code and make sure to push them to the feature branch of your fork.

Commit all code changes to your feature branch and upload them:

```shell
$ git push origin <NAME_OF_BRANCH>
```

## Start a code review

Once you think your changes are ready, you start the review process.  There are few ways of doing that,
one is to use the [Github web UI](https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).
Visit the [project](https://github.com/google/picatrix/pulls) and click the `create a pull request` button.

The other option is to use the Github CLI tool.

Select a good descriptive PR name and write a description describing the change. After all is completed, select a code reviewer
from the list of available reviewers (if you don't have the option to select a reviewer, one will be
assigned).

## Status checks
Once your pull request has been created, automated checkers will run to on your changes to check
for mistakes, or code that doesn't match the style guide. Review the output from the tools, and
make sure your pull request passes.

Your pull request cannot be merged until the checkers report everything is OK.

## Making changes after reviews

Your pull request will be assigned to a project maintainer either by you or the reviewer. 
The maintainer will review your code, and may push some changes to your branch and/or request
that you make changes. If they do make changes, make sure your local copy of the branch 
(git pull) before making further changes.

After they've reviewed your code, make any necessary changes, and push them to your
feature branch. After that, reply to the comments made by the reviewer, then request
a new review from the same reviewer. In the upper right corner in the `Reviewers`
category a button should be there to re-request a review from a reviewer (ATM it is a circle, 
or arrows that make up a circle).

## Merging
Once the pull request assignee is happy with your proposed changes, and all the status
checks have passed, the assignee will merge your pull request into the project. 
Once that's completed, you can delete your feature branch.
