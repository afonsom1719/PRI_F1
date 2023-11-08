### QRELS1_Constructor
- This qrel i related to the query 1, where it should find all constructors who have british nationality and has the year 1990 mentioned in their bio (constructor_bio)
- All the qrels that were added were found in the `constructors.json` file and not retrieved by the solr `query select` because the year is like `1990s` instead of `1990s`
- There is one qrel that appear 2 times bacase although the constructor bio is the same, they are two 'different' constructors with different ids (`187`, `188`, `198`) and names (`McLaren-Ford`, `McLaren-Serenissima`, `McLaren-Alfa Romeo`)

### QRELS2_seasons
