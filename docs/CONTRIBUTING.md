# Contributing to Great Wall

First off, thank you for considering contributing to Great Wall. It's people like you that make Great Wall such a great tool.

## Where do I go from here?

If you've noticed a bug or have a feature request, make one! It's generally best if you get confirmation of your bug or approval for your feature request this way before starting to code.

## Fork & create a branch

If this is something you think you can fix, then fork Great Wall and create a branch with a descriptive name.

A good branch name would be (where issue #325 is the ticket you're working on):

```sh
git checkout -b 325-add-japanese-translations

Get the test suite running
Make sure you have Python installed and the test suite runs without any errors.

Implement your fix or feature
At this point, you're ready to make your changes! Feel free to ask for help; everyone is a beginner at first.

Make a Pull Request
At this point, you should switch back to your master branch and make sure it's up to date with Great Wall's master branch:

git remote add upstream git@github.com:original/greatwall.git
git checkout master
git pull upstream master


Then update your feature branch from your local copy of master, and push it!


git checkout 325-add-japanese-translations
git rebase master
git push --set-upstream origin 325-add-japanese-translations

Go to the Great Wall repo and press the "Compare & pull request" button.

Keeping your Pull Request updated
If a maintainer asks you to "rebase" your PR, they're saying that a lot of code has changed, and that you need to update your branch so it's easier to merge.

To learn more about rebasing in Git, there are a lot of good resources but here's the suggested workflow:
git checkout 325-add-japanese-translations
git pull --rebase upstream master
git push --force-with-lease 325-add-japanese-translations


Merging a PR (maintainers only)
A PR can only be merged into master by a maintainer if:

It is passing CI.
It has been approved by at least two maintainers. If it was a maintainer who opened the PR, only one extra approval is needed.
It has no requested changes.
It is up to date with current master.
Any maintainer is allowed to merge a PR if all of these conditions are met.

Shipping a release (maintainers only)
Maintainers need to do the following to push out a release:

Pull latest code from master
Update the version number in __init__.py
Create a new git tag for the version number
Push the git tag to the repo
Build and upload the package to PyPI


This guide should help new developers to understand how they can contribute to the Great Wall project.