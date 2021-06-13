# Bash Scripts Testing

The `bats` framework is included and used to test the scripts included, specifically the scripts designed to parse through the logging output. As this involves delicate regex and indexes, it is necessary to test these.

## Running Tests

Running the tests are easy, and can be done with a single command. Once the working directory is this directory, run the following command.

```bash
./bats/bin/bats *.bats
```

This will run all test files that have the `.bats` suffix.
