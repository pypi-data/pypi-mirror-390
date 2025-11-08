# Unit Tests

Run a test with VS Code [R Test Adapter](https://marketplace.visualstudio.com/items/?itemName=meakbiyik.vscode-r-test-adapter) or via the command line, for example:

```
Rscript -e "testthat::test_file('tests/testthat/test-missing-months.R')"
```

To run all unit tests via the CLI, run `Rscript -e devtools::test()`

Each unit test calls a setup method to create the necessary directories and mock input data, then calls the script and verifies the output is as expected.


For more information, see https://r-pkgs.org/testing-basics.html
