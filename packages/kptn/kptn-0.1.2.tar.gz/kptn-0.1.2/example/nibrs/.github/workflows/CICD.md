# CI/CD

The workflow desired for our CI/CD is as follows:

1. When you make a merge request both the linting and test actions will trigger.
    * The linting actions will be status check in the merge request, blocking until good.
    * The test action will NOT be a status check and the developer should verify that the test pass
1. Everytime you commit the linting actions will run again and update their status checks in real time.
    * The test action will NOT be re-run
1. Once the MR is in a finished state the developer should manually trigger a test action (see below for instructions)
    * It is the reviewers responsibility to confirm there is a passing test action before approving the merge request

### Running test actions manually

To run the test actions you should:

1. Navigate to the repository in github and go to the `Actions` tab.
1. In the left `Actions` navbar select `Manual Run - Tests`
1. In the main workflow run table press the `Run workflow` dropdown
1. In the `Use workflow from` dropdown select the branch
1. Press the `Run workflow` button.