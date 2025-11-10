To run the test suite for this library, first download the files found at (Github)[https://github.com/douglassimonsen/pbi_core/releases/tag/resources]. SSAS operations depend on Windows OS APIs, so they can only be run on Windows computers.

You should have the following files:

- multilang_example.xlsx
- test.pbix
- test_ssas.pbix

Then navigate to your copy of `pbi_core` and create a subfolder named `example_pbis`. Copy all 3 files to this new folder.

Then run 

```shell
pytest .
```


!!! note Quicker Testing

    There are currently a few side-tests that take a disporportionate amount of time to run. To skip these tests, run 

    ```shell
    pytest . -m "not slow"
    ```