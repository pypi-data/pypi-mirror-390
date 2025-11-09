# ExactPy

A modern, highly configurable Python interface to the Exact Online API based on `Pydantic` and `httpx` and integrates with `sparkdantic` to make it easy to convert your data to `(py)spark` dataframes.

For now, this package _does not_ provide any controller methods `POST` and `PUT` calls; it's basically read-only. This will be added later.

## Installing

You can install directly from PyPI using e.g.

```bash
uv add exactpy
```

or

```bash
pip install exactpy
```

or you can install locally from file using:

```bash
uv pip install -e <location_on_disk>
```

## Developing

This repo provides a devcontainer to easily develop the package. It assumes you have `uv` and `fish` installed on your host system. This cannot be made optional because these assumptions involve bind mounts.

Install the package locally (symlinked) within the `venv` created by `uv` using:

```bash
uv pip install -e .
```

### Pre-commit

We use `pre-commit` to run a few hooks to ensure code quality and stuff like that. Please use the devcontainer, all this is taken care for you if you do so.

### Running tests

We use `tox` for bothing running the tests as well as running `pre-commit`. Please run `tox` to run your tests.

## Contributing

Please see `CONTRIBUTING.md`.

## Issues

If you discover bugs or other issues, please create an issue with a stack trace and code to reproduce. We have no predefined format for issues, just make sure there is enough info to reproduce.

## Why?

Currently available packages aren't configurable in such a way that they are usable to me. This package attempts to fix that.

## Good to know

### Spark and context aware serialization

This package provides support for conversion to Spark dataframes indirectly, by using `SparkModel` instead of `BaseModel`, Spark schemas can be generated from models (see also: https://github.com/mitchelllisle/sparkdantic) by callign e.g. `exactpy.models.financial.GLAccountModel.model_spark_schema()`.

The types used in `OData` are a bit unusual in some cases. The timestamp type is a string with a timestamp in millisecond precision embedded into it, for instance.

For this reason, serialization output can be changed to be (among other things) `(py)spark` and `pandas` compatible. This can be done by passing a context to the serialization methods. One example:

```python
gl_account_instance.model_dump(by_alias=False, context={"output": "spark"})
```

For now, this does not change much (only timestamps are serialized as `datetime.datetime` instead of timestamp strings), but this might change in the future. Just pass `context={"output": "spark"}` in your serialization methods, and you're good.

### Model field naming

This package uses Pydantic's `BaseModel` (well, actually `sparkdantic.SparkModel`, but that is derived from `BaseModel`) as model base classes. Field names _do not_ correspond exactly to Exact Online API field names. ExactOnline uses a special type of pascal case. This means that all words are capitalized, like in regular pascal case. It differs in the way it handles acryonyms. For example, `user_id` (snake case) would normally become `UserId` in pascal case. In Exact Online syntax, this becomes `UserID`.

Similarly, for longer acronyms such as the one found in `oid_connect`, this will become `OIDConnect` in Exact Online syntax.

Because Pydantic is very pythonic, it's customary to use snake case for property (field) names. Here's is the issue with that: when converting pascal case from the Exact Online API responses to snake case, information is lost. For example: `UserID` will be come `user_id` when using e.g. Pydantic's `to_pascal` validation. To solve this, a special type of snake case is used in the `exactpy`'s model definition. Every acronym is suffixed with a double underscore `__`, which tells the validator to capitalizer every single letter before the underscore, until it hits the beginning of the string or another underscore.

As an example: Exact Online's field with name `GLAccountID` is defined in our models as `gl__acount_id__`.

One exception is the `id` field in every model, which is always completely capitalized. The reason for this, is that it's so common, it would be a waste of time to double underscore it in every single model.

## Sample usage

### Initial oauth token request

This initial token request theoretically needs to be done once. An access token and requets token will be available after this. If the access token is refreshed in time (refresh token is valid for 30 days max), no log in has to be performed.

```python
from exactpy.client import Client

client_id = "***"
client_secret = "***"

# This can be anything, but it needs to satisfy two conditions:
# 1. It needs to be a valid public website
# 2. It needs to be website protected by an SSL certificate (https)
# It needs to match exactly what you entered in your app registration
redirect_url = "https://some_site"

client = Client(
    client_id=client_id, client_secret=client_secret, redirect_url=redirect_url
)

# This will print a link that you can click
# You'll have to log to the Exact Online portal first
# You'll get redirected to `redirect_url`, and you'll need to copy that url
print(client.auth_client.get_authorization_url())

# Enter the url that you've copied earlier and hit enter
resp_url = input()

# If everything went well, you should now be able to acquire
# a token and refresh token with the line below
# This will also automatically cache your credentials
# to file, if caching is enabled (which it is, by default)
client.auth_client.acquire_token(resp_url)
```

If your cache callable was not set to `None`, your credentials should now have been saved. In the default case, they're saved in `creds.json` (plain text).

### Client usage

Now you can use the client like below:

```python
from exactpy.client import Client
from pprint import pprint

client = Client(
    client_id="xxx",
    client_Secret="xxx,
    verbose=True,
)

# (Almost) every request requires a division to be set
# This division number is set as a client property
# and set with every request, as part of the url
# You can set the division equal to the current divison
# (current as in server side) using:
client.set_initial_division()

# Print the division using:
pprint(client.get_current_division().model_dump(by_alias=True))

# Alternatively, you may pick a different division by listing them
# and selecting a specific one:
divisions = client.system.divisions.all()

# Select the "nth" division and set it as current division
# n = 0...len(divisions)-1
client.division = divisions[n].code

# Every request you do, will trigger a token
# check as well. In the default case, auto-caching is done
# This means that the current access token and refresh token
# (after a optional refresh) are cached. This is only true
# if cache_callable was not set to None.
# To disable this behaviour, either set cache_callable to None
# or set autocache_enabled to False.

# Note that endpoint controllers are namespaced by service,
# as shown below (general ledger accounts are part of the
# financial service) and above (divisions are part of the)
# system service
gl_accounts = client.financial.gl_accounts.all()
```

## Detailed usage

Every `OData` query arg is supported, except `$skip`; this is because `Exact Online` does not support this. See also: https://support.exactonline.com/community/s/knowledge-base#All-All-DNO-Simulation-query-string-options

Okay fine, on some older endpoints it might actually be supported, but I'm not going to find out which ones those are.

### Filters

Filters are based on exact value matches. Filter field names should use the model field names, not the Exact Online API field names.
These field names are automatically translated into their Exact Online name variant. Multiple filters are combined using the binary `and` or the binary `or` operator, which can be set using the `FilterOperatorEnum` enum type. Example:

````python
from exactpy.types import FilterOperatorEnum

# OR
reporting_balances = client.financial.reporting_balances.all(
    filters={"reporting_year": 2011, "division": 12},
    filter_operator=FilterOperatorEnum.OR,
)

# AND
reporting_balances = client.financial.reporting_balances.all(
    filters={"reporting_year": 2011, "division": 12},
    filter_operator=FilterOperatorEnum.AND,
)
```

Obviously, because they're enums, you can also use the enum values themselves. Example:


```python

reporting_balances = client.financial.reporting_balances.all(
    filters={"reporting_year": 2011, "division": 12},
    filter_operator="and", # use "and" or "or" (enum values)
)
```

### Top n results
Use the `top` argument to select the first `top` results:

```python

# This should give maximum (for two reasons, more on this later) 5 results
reporting_balances = client.financial.reporting_balances.all(top=5)
````

### Expand

Embedded models are _not expanded_ by default. Use the `expand` arg to tell the API to expand them. Again, using model field names, not Exact Online API field names. Example:

```python
accounts = client.crm.accounts.all(expand=["bank_accounts"])
```

### Select

Use the `select` arg to only retrieve a select number of columns. Again, using model field names, not Exact Online API field names. Example:

```python
gl_accounts = client.financial.gl_accounts.all(select=["reporting_year"])
```

### Inline count

Setting `inline_count` to `True` will retrieve the count of all records. In the client this will result in a `tuple` as return type, instead of a simple list of model instances:

```python
gl_accounts, count = client.financial.gl_accounts.all(select=["reporting_year"], inline_count=True)
```

### Count only

`OData` also implements a `$count` query arg to only retrieve a count of all records. This is implemented as the `count()` method on the controllers in this package. No options can be set, except for `include_division`, which will tell the client to include the division in the API url or not. Example:

```python
count = client.financial.gl_accounts.count()
```

### Paged (generator) vs all results

The underlying way for retrieving records is using a generator that yields every retrieved page as a results list. This is implemented as the `all_paged` method on the controllers. Example usage:

```python
for page in client.financial.gl_accounts.all_paged(select=["reporting_year"]):
    for gl_account in page:
        print(page.model_dump(by_alias=True))
```

And using inline count:

```python
for page, count in client.financial.gl_accounts.all_paged(select=["reporting_year"], inline_count=True):
    print(f"Total count: {count}")
    for gl_account in page:
        print(page.model_dump(by_alias=True))
```

Note that the count given every yield by the generator is the total count, and is the same every time. It is not the count per page.

### Max pages

Setting the `max_pages` arg will result in only retrieving `max_pages` from the API. This competes with the `top` argument. If either one exhausts the number results first, the other isn't effective, obviously.

Note that when you set `inline_count=True`, the API responses are no longer paged and this argument will not do anything at all.

### Skipping invalid

By default, invalid records are skipped. This is not the default pydantic behaviour. Lists of input is usually parsed using for example:

```python
list_adapter = TypeAdapter(SomeModel)
list_adapter.validate_python([{"field1": "someval", ...}, ...])
```

This will raise a `pydantic.ValidationError` when it encounters invalid input (ie input that cannot be validated using that specific model).

This is not really wanted behavior when using the Exact Online API in combination with the strict Pydantic models in this package, as it's very clear that Exact Online API output is known not to adhere to field types described in the API (notoriously, types will sometimes have undocumented values).

Setting `skip_invalid=True`, will skip over these records and log these events (if `verbose=True` on the client). Setting `skip_invalid=False` will result in normal pydantic behavior.
