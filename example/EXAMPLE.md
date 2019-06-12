User Guide
==========

# 1. Sign Up / Sign in

```bash
    open https://client.praktikos.com
```

# 2. Generate Code from example swagger file

   * In the browser window side panel, Click "Generate Code"
   * Click in dashed line box "Drag SWAGGER JSON file here..."
   * Navigate to the file: praktikos-python-rdb/example/swagger.json
   * Click the "Next" button
   * Click the "Finish" button after generated code is downloaded

# 3. Merge generated code into main project

open up a Terminal (shell) window

```bash
cd praktikos-python-rdb/example
./merge_after_codegen.sh
```

# 4. Publish API from newly generated code

   * Zip up the main project (merged) ~/praktikos-python-rdb.zip
   * In the browser window side panel, Click "Publish API"
   * Click in dashed line box "Drag Zip file here..."
   * Navigate to the file: praktikos-python-rdb.zip
   * Click the "Next" button
   * Click on "LambdaApiGenerated"
   * Click the "Next" button
   * wait patiently about a minute
   * Click the "Finish" button after API is provisioned and published
   
# 5. Test RESTful API

open up a Terminal (shell) window

```bash
cd praktikos-python-rdb/example
./test_published.sh
```
